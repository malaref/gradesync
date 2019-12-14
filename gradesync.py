from re import search

CONFIG_FIELDS = ({'name': 'spreadsheet_url', 'label': 'Spreadsheet URL', 'pattern': '.*[-\\\\w]{25,}.*'},
                 {'name': 'sheet_name', 'label': 'Sheet Name', 'pattern': '.*'},
                 {'name': 'header_row', 'label': 'Header Row', 'pattern': '[0-9]+'},
                 {'name': 'full_mark_row', 'label': 'Full Mark Row', 'pattern': '[0-9]+'},
                 {'name': 'first_row', 'label': 'First Row', 'pattern': '[0-9]+'},
                 {'name': 'last_row', 'label': 'Last Row', 'pattern': '[0-9]+'},
                 {'name': 'emails_column', 'label': 'Emails Column', 'pattern': '[A-Z]+'},
                 {'name': 'grades_columns', 'label': 'Grades Columns (space-separated)', 'pattern': '([A-Z]+ )*[A-Z]+'})


def list_resource(classroom, path, **params):
    resource = classroom
    for node in path:
        resource = getattr(resource, node)()
    response = resource.list(**params).execute()
    items = response.get(path[-1])
    while 'nextPageToken' in response:
        response = resource.list(pageToken=response['nextPageToken'], **params).execute()
        items.extend(response.get(path[-1]))
    return items


def get_courses(classroom):
    return list_resource(classroom, ('courses',))


def sync(sheets, classroom, config):
    spreadsheet_id = search(r'[-\w]{25,}', config['spreadsheet_url'])[0]
    
    def get_value(row, column):
        return sheets.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'{config["sheet_name"]}!{column}{row}').execute().get('values')[0][0]
    
    def get_values(column):
        return tuple(row[0] if row else None for row in sheets.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'{config["sheet_name"]}!{column}{config["first_row"]}:{column}{config["last_row"]}').execute().get('values'))
    
    def get_or_create_course_work_id(title, max_points):
        for course_work in course_works:
            if course_work['title'] == title:
                return course_work['id'], f'Full mark mismatch for {title}' if course_work['maxPoints'] != max_points else None
        new_course_work = classroom.courses().courseWork().create(courseId=config['course_id'], body={
            'title': title,
            'state': 'PUBLISHED',
            'workType': 'ASSIGNMENT',
            'assigneeMode': 'ALL_STUDENTS',
            'maxPoints': max_points
        }).execute()
        return new_course_work['id'], f'Created new assignment for {title}'
    
    log = []
    
    sheet_emails = get_values(config['emails_column'])
    classroom_emails = {student['userId']: student['profile']['emailAddress'] for student in list_resource(classroom, ('courses', 'students'), courseId=config['course_id'])}
    course_works = list_resource(classroom, ('courses', 'courseWork'), courseId=config['course_id'])

    # Syncing grades!
    for column in config['grades_columns'].split():
        title = get_value(config['header_row'], column)
        max_points = int(get_value(config['full_mark_row'], column))
        grades = dict(zip(sheet_emails, get_values(column)))
        course_work_id, class_work_log = get_or_create_course_work_id(title, max_points)
        if class_work_log:  log.append(class_work_log)
        student_submissions = list_resource(classroom, ('courses', 'courseWork', 'studentSubmissions'), courseId=config['course_id'], courseWorkId=course_work_id)
        for student_submission in student_submissions:
            student_id = student_submission['userId']
            student_email = classroom_emails[student_id]
            grade = grades.pop(student_email, None)
            if grade is None:
                log.append(f'No grade for {student_email} in {title}')
                continue
            classroom.courses().courseWork().studentSubmissions().patch(
                courseId=config['course_id'], courseWorkId=course_work_id, id=student_submission['id'], updateMask='draftGrade',
                body={'draftGrade': float(grade)}).execute()
        if grades:
            for email in grades:
                log.append(f'Found {email} in {title} but not in the classroom')
    
    return log
