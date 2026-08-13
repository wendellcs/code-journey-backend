from fastapi import APIRouter, Depends, status, HTTPException
from schemas.studentsSchema import StudentsSchema, EditStudentSchema, StudentSkillSchema, EditStudentSkillSchema
import psycopg2
from database import get_connection, count_rows
import math
from security import verify_token

router = APIRouter(prefix='/students')

@router.get('', status_code=status.HTTP_200_OK)
def get_students(search: str = None, limit: int = 4, page: int = 1, filter:str = 'created_at', db = Depends(get_connection)):
    _, cursor = db 
    
    if limit < 2:
        limit = 2
        
    offset = (page - 1) * limit
    
    if filter != 'created_at' and filter != 'first_name':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid filter. Allowed values are: created_at, first_name.')
    
    where_clause = ''
    
    if search:
        where_clause = 'WHERE first_name ILIKE %s'
        search_term = f'%{search}%'
        execute_values = (search_term, limit, offset)
    else:
        execute_values = (limit, offset)
        
    cursor.execute(f'SELECT * FROM students {where_clause} ORDER BY {filter} LIMIT %s OFFSET %s',
        execute_values)
    
    students = cursor.fetchall()
    total_students = count_rows(cursor, 'students', where_clause, search_term if search else '')

    return {
        'students': students,
        'current_page': page,
        'total_pages': math.ceil(total_students / limit)
    }


@router.get('/all', status_code=status.HTTP_200_OK)
def get_all_students(db = Depends(get_connection)):
    _, cursor = db
    
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    
    return students
    
    
@router.get('/{student_id}/skills', status_code=status.HTTP_200_OK)
def get_student_skills(student_id: str, db = Depends(get_connection)):
    _, cursor = db 
    
    cursor.execute('''SELECT student_skills.*, technologies.name, technologies.tech_icon
        FROM student_skills JOIN technologies ON student_skills.technology_id = technologies.id
        WHERE student_skills.student_id = %s''', (student_id,))
    
    student_skills = cursor.fetchall()
    
    return student_skills
    
    
@router.get('/{student_id}/skills/summary', status_code=status.HTTP_200_OK)
def get_students_skill_summary(student_id: str, db = Depends(get_connection)):
    _, cursor = db 
    
    cursor.execute('''SELECT student_skills.*, technologies.name, technologies.tech_icon 
                   FROM student_skills JOIN technologies ON student_skills.technology_id = technologies.id
                   WHERE student_skills.student_id = %s and independence_level > 0''', (student_id,))

    student_skills = cursor.fetchall()
    return student_skills


@router.get('/leaders', status_code=status.HTTP_200_OK)
def get_leaders(db = Depends(get_connection)):
    _, cursor = db 
    
    cursor.execute('''SELECT 
            students.id, 
            students.first_name, 
            students.last_name, 
            classes.module, 
            COUNT(*) as topics_mastered,
            SUM(student_skills.independence_level) as points
            FROM student_skills
            JOIN students ON student_skills.student_id = students.id
            JOIN classes ON students.class_id = classes.id
            WHERE student_skills.independence_level > 2
            GROUP BY students.id, students.first_name, students.last_name, classes.module
            ORDER BY points DESC''')
    
    students = cursor.fetchall()
    
    students_by_modules = {}
    
    for student in students:
        module = student['module']
        if module not in students_by_modules:
            students_by_modules[module] = []
        
        if len(students_by_modules[module]) >= 2:
            continue
        
        students_by_modules[module].append(student)
    
    module_list = ['Young 1', 'Young 2', 'Young 3', 'Young 4']
    
    for module in module_list:
        if module not in students_by_modules:
            students_by_modules[module] = [{
                'first_name': 'Bot',
                'last_name': 'Mariza',
                'module': module,
                'topics_mastered': 3,
                'points': 15
            }, {
                'first_name': 'Bot',
                'last_name': 'Mina',
                'module': module,
                'topics_mastered': 2,
                'points': 10
            }]
        
    students_by_modules = dict(sorted(
        students_by_modules.items(),
        key=lambda item: int(item[0].split()[-1])
    ))
        
    return students_by_modules
    
@router.post('/add', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
def create_student(student_data: StudentsSchema, db = Depends(get_connection)):
    connection , cursor = db 
    
    try:
        cursor.execute('INSERT INTO students (first_name, last_name, age, class_id, tag, current_module) VALUES (%s, %s, %s, %s, %s, %s)',
            (student_data.first_name, student_data.last_name, student_data.age, student_data.class_id, student_data.tag, student_data.current_module))
        connection.commit()
    except psycopg2.errors.CheckViolation:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Age must be greater than 12.')
    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='The chosen tag is already being used.')
    except psycopg2.errors.ForeignKeyViolation:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The referenced class was not found.')


@router.post('/{student_id}/skills', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
def set_student_skill(student_id: str, skill_data: StudentSkillSchema, db = Depends(get_connection)):
    connection, cursor = db

    execute_values = [student_id, skill_data.technology_id, skill_data.independence_level]
    insert_clause = 'student_id, technology_id, independence_level'
    values_clause = '%s, %s, %s'
    
    if skill_data.notes:
        execute_values.append(skill_data.notes)
        insert_clause += ', notes'
        values_clause += ', %s'
        
    try:
        cursor.execute(f'INSERT INTO student_skills ({insert_clause}) VALUES ({values_clause})',
            (*execute_values,))
        connection.commit()
        
    except psycopg2.errors.ForeignKeyViolation:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The referenced student was not found.')
    
    
@router.patch('/{id}/skills', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def edit_student_skills(id: str, student_skill_data: EditStudentSkillSchema, db = Depends(get_connection)):
    connection, cursor = db
    clauses = []
    execute_values = []
    
    if student_skill_data.independence_level is not None:
        clauses.append('independence_level = %s')
        execute_values.append(student_skill_data.independence_level)
        
    if student_skill_data.notes is not None:
        clauses.append('notes = %s')
        execute_values.append(student_skill_data.notes)
    
    set_clause = ', '.join(clauses)
    
    if not clauses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough data")
    
    try:
        cursor.execute(f'UPDATE student_skills SET {set_clause} WHERE id = %s', (*execute_values, id))
        
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student not found')
        connection.commit()
    except psycopg2.errors.DataError: 
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Invalid data format')
    
    return {'ok': 'Skill successfully updated.'}


@router.patch('/edit', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def edit_student(new_data: EditStudentSchema, db = Depends(get_connection)):
    connection, cursor = db
    clauses = []
    execute_values = []

    if new_data.first_name:
        clauses.append('first_name = %s')
        execute_values.append(new_data.first_name)
    if new_data.last_name:
        clauses.append('last_name = %s')
        execute_values.append(new_data.last_name)
        
    if new_data.current_module:
        clauses.append('current_module = %s')
        execute_values.append(new_data.current_module)
        
    if new_data.tag:
        clauses.append('tag = %s')
        execute_values.append(new_data.tag)
        
    set_clause = ', '.join(clauses)

    try:
        cursor.execute(f'UPDATE students SET {set_clause} WHERE id = %s', (*execute_values, new_data.id))
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student not found')
        
        connection.commit()
    except psycopg2.errors.DataError: 
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Invalid data format')
    
    
@router.delete('/remove/{student_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(verify_token)])
def delete_student(student_id: str, db = Depends(get_connection)):
    connection, cursor = db
    
    cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
        
    if cursor.rowcount == 0:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student not found')
    
    connection.commit()
    
    return {'ok': 'Student successfully deleted.'}