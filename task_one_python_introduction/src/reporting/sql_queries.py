# Создание индексов на столбцы таблицы students
SQL_CREATE_INDEXES = """
    CREATE INDEX IF NOT EXISTS idx_students_room_id ON students (id);
    CREATE INDEX IF NOT EXISTS idx_students_birthday ON students (birthday);
"""

# Вставка новых значение в таблицу rooms
SQL_ROOMS_INSERTION = "INSERT INTO rooms (id, name) VALUES (%s, %s);"

# Вставка новых значение в таблицу students
SQL_STUDENTS_INSERTION = "INSERT INTO students (id, name, birthday, sex, room) VALUES (%s, %s, %s, %s, %s);"

# 1. Список комнат и количество студентов в каждой из них
SQL_STUDENTS_PER_ROOM = """
SELECT
    r.name AS room_name,
    COUNT(s.id) AS student_count
FROM
    rooms r
LEFT JOIN
    students s ON r.id = s.room
GROUP BY
    r.name
ORDER BY
    student_count DESC;
"""

# 2. 5 комнат, где самый маленький средний возраст студентов

SQL_SMALLEST_AVG_AGE = """
SELECT
    r.name AS room_name,
    ROUND(AVG(EXTRACT(YEAR FROM AGE(s.birthday))), 2) AS avg_age
FROM
    rooms r
JOIN
    students s ON r.id = s.room
GROUP BY
    r.name
ORDER BY
    avg_age ASC
LIMIT 5;
"""

# 3. 5 комнат с самой большой разницей в возрасте студентов
SQL_LARGEST_AGE_DIFF = """
SELECT
    r.name AS room_name,
    MAX(EXTRACT(YEAR FROM AGE(s.birthday))) - MIN(EXTRACT(YEAR FROM AGE(s.birthday))) AS age_difference
FROM
    rooms r
JOIN
    students s ON r.id = s.room
GROUP BY
    r.name
HAVING
    COUNT(s.id) >= 2 -- Требуется минимум два студента для разницы
ORDER BY
    age_difference DESC
LIMIT 
    5;
"""

# 4. Список комнат где живут разнополые студенты
SQL_MIXED_SEX_ROOMS = """
SELECT
    r.name AS room_name
FROM
    rooms r
JOIN
    students s ON r.id = s.room
GROUP BY
    r.name
HAVING
    COUNT(DISTINCT s.sex) > 1 -- Количество уникальных значений пола в комнате больше одного
ORDER BY
    r.name;
"""
