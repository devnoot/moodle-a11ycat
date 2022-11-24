from decouple import config
import requests as req
import subprocess
from clint.textui import progress
import os

MOODLE_TOKEN = config('MOODLE_TOKEN')
MOODLE_URL = config('MOODLE_URL')
MOODLE_WS_URL = MOODLE_URL + '/webservice/rest/server.php'
MOODLE_COURSE_ID = config('MOODLE_COURSE_ID')
DATA_PATH = 'data'


def init():
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)


def download_file(url, dest):
    print(f'Downloading file to {dest}')

    r = req.get(url, stream=True, params={
                'forcedownload': 1, 'token': MOODLE_TOKEN})
    with open(dest, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()
    return dest


def core_course_get_contents(course_id):
    qs = {
        'wstoken': MOODLE_TOKEN,
        'wsfunction': 'core_course_get_contents',
        'moodlewsrestformat': 'json',
        'courseid': course_id,
    }
    r = req.get(MOODLE_WS_URL, params=qs)
    return r.json()


def core_course_get_courses(course_id):
    qs = {
        'wstoken': MOODLE_TOKEN,
        'wsfunction': 'core_course_get_courses',
        'moodlewsrestformat': 'json',
        'options[ids][1]': course_id
    }
    r = req.get(MOODLE_WS_URL, params=qs)
    return r.json()


def process_course(course_id):

    # Get the course contents
    course_contents = core_course_get_contents(course_id)

    # Extract the pdf files from the course contents
    files = []
    for section in course_contents:
        for module in section['modules']:
            if module['modname'] == 'resource':
                files.append(module['contents'][0])

    # extract the pdf files from the course contents
    pdfs = []
    for file in files:
        if file['filename'].endswith('.pdf'):
            pdfs.append(file)

    # process the pdf files
    for pdf in pdfs:
        # download the pdf
        pdf_url = pdf['fileurl']
        pdf_name = pdf['filename']
        # each pdf should have their own directory
        file_dir = os.path.join(DATA_PATH, str(pdf_name).replace('.pdf', ''))
        pdf_path = os.path.join(file_dir, pdf_name)
        # create the directory if it doesn't exist
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        download_file(pdf_url, pdf_path)
        # pdftohtml -s -zoom 1 -nomerge
        subprocess.run(['pdftohtml', '-s', '-zoom', '1',
                       '-nomerge', pdf_name], cwd=file_dir)

        # The html file is saved as pdf_name-html.html
        # there is a second file generated that is not needed
        html_file = os.path.join(pdf_name.replace('.pdf', '-html.html'))
        print(html_file)
        print(f'Generating a11y report for {html_file}')
        subprocess.run(['sniff', '-l', '.', '-q', '', html_file], cwd=file_dir)

    # call the 'core_course_get_contents' web service
    pass


def main():
    init()
    process_course(course_id=MOODLE_COURSE_ID)
    pass


if __name__ == '__main__':
    main()
