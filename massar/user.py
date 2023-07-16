from datetime import datetime
import json
import os
import pickle
import re
from bs4 import BeautifulSoup as bs, Tag
from model.cycle import Cycle
from model.education import Education
from model.level import Level
from model.quiz import Quiz
from model.section import Section
from massar.session import CACHE_DIR, COOKIE_FILE, __sess__
from model.session import Session
from model.student import Student
from model.subject import Subject
from utils.html import parse_table




HOSTNAME = 'massar.men.gov.ma'

CULTURE_URL = f'https://{HOSTNAME}/General/SetCulture?culture='
DASHBOARD_URL = f'https://{HOSTNAME}/Dashboard'
ACCOUNT_URL = f'https://{HOSTNAME}/Account'
STUDENTS_URL = f'https://{HOSTNAME}/Evaluation/EspaceEnseignant/ListeEleves'
STUDENTS_API_URL = f'{STUDENTS_URL}/Search'
GRADES_URL = f'https://{HOSTNAME}/Evaluation/GestionDesNotes/SaisiedesNotesParMatiere'
GRADES_API_URL = f'https://{HOSTNAME}/Evaluation/GestionDesNotes/SaisiedesNotesParMatiere/GetListNotesParMatiere'
FILTER_SUBJECTS_API_URL = f'https://{HOSTNAME}/Evaluation/GestionDesNotes/SaisiedesNotesParMatiere/FiltreMatiere'
FILTER_GRADES_API_URL = f'https://{HOSTNAME}/Evaluation/GestionDesNotes/SaisiedesNotesParMatiere/FiltreNotecc'

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.educations = {}
        self.cycles = {}
        self.sessions = {}
        self.subjects = {}
        self.by_education_cycle = {}
        self.by_levels = {}
        self.by_sections = {}
        self.by_students = {}

    def login(self):
        if self.is_logged_in(): return self

        html = __sess__.get(ACCOUNT_URL).text
        doc = bs(html, 'html.parser')
        token = doc.find('input', {'name': '__RequestVerificationToken'}).get('value')
        __sess__.post(ACCOUNT_URL, data={
            '__RequestVerificationToken': token,
            'UserName': self.username,
            'Password': self.password,
        })
        # save headers cookies
        os.makedirs(CACHE_DIR, exist_ok=True)
        pickle.dump(__sess__.cookies, open(COOKIE_FILE, 'wb'))
        return self
    
    def set_language(self, lang):
        self.login()
        assert lang in ['ar', 'fr']
        __sess__.head(CULTURE_URL + lang)
        return self

    
    def is_logged_in(self):
        return __sess__.head(DASHBOARD_URL).status_code == 200
    
    def scrap_sessions(self, html=None, check_login=True):
        if check_login and not self.is_logged_in():
            print('Not logged in, logging in...')
            self.login()

        html = html or __sess__.get(GRADES_URL).text
        doc = bs(html, 'html.parser')
        for option in doc.find('select', {'id': 'IdSession'}).find_all('option'):
            session = Session(id=option.get('value'), name=option.text)
            self.sessions[session] = session
        return self
    
    def scrap_subjects(self):
        self.scrap_sessions()

        lvl: Level
        for lvl in self.by_levels.values():
            data = __sess__.post(FILTER_SUBJECTS_API_URL, data={'Niveau': lvl.id}).json()
            
            for subject in data:
                subj_id = subject['Value']
                subject = Subject(
                    id=subject['Value'],
                    name=subject['Text'],
                    levels=set(),
                    sessions=self.sessions
                ) if subj_id not in self.subjects else self.subjects[subj_id]

                subject.levels.add(lvl)

                self.subjects[subject.id] = subject

        return self
    
    def scrap_educations(self, html=None, check_login=True):
        if check_login and not self.is_logged_in():
            print('Not logged in, logging in...')
            self.login()

        html = html or __sess__.get(STUDENTS_URL).text
        doc = bs(html, 'html.parser')
        for option in doc.find('select', {'id': 'TypeEnseignement'}).find_all('option'):
            edu = Education(id=option.get('value'), name=option.text)
            self.educations[edu.id] = edu
        return self
    
    def scrap_cycles(self, html=None, check_login=True):
        if check_login and not self.is_logged_in():
            print('Not logged in, logging in...')
            self.login()

        html = html or __sess__.get(STUDENTS_URL).text
        cycles_str = re.search(r'var CyclesEtab ?= ?(\[.+\]);', html).group(1)
        
        cycles_json = json.loads(cycles_str)
        for cycle in cycles_json:
            cyc = Cycle(
                id=cycle['Value'],
                name=cycle['Text'],
            )
            self.cycles[cyc.id] = cyc

        return self
    
    def scrap_levels(self, html=None, check_login=True):
        if check_login and not self.is_logged_in():
            print('Not logged in, logging in...')
            self.login()

        html = html or __sess__.get(STUDENTS_URL).text

        self.scrap_educations(html, check_login=False)
        self.scrap_cycles(html, check_login=False)

        levels_str = re.search(r'var ListeNiveau ?= ?(\[.+\]);', html).group(1)
        
        levels_json = json.loads(levels_str)
        for level in levels_json:
            edu_id = str(level['id_typeEnseignement'])
            lvl = Level(
                id=level['nefstat'],
                name=level['libformat'],
                education=self.educations[edu_id],
                cycle=self.cycles[level['CD_CYCLE']],
                sections={}
            )
            self.by_education_cycle[edu_id, level['CD_CYCLE']] = lvl
            self.by_levels[lvl.id] = lvl

        return self
    
    def scrap_sections(self, html=None, check_login=True):
        if check_login and not self.is_logged_in():
            print('Not logged in, logging in...')
            self.login()

        self.scrap_levels(html, check_login=False)

        html = html or __sess__.get(STUDENTS_URL).text
        sections_str = re.search(r'var ListeClasse ?= ?(\[.+\]);', html).group(1)
        
        sections_json = json.loads(sections_str)
        for sec in sections_json:
            lvl: Level = self.by_levels[sec['nefstat']]
            sect = Section(
                id=sec['idClasse'],
                name=sec['LibelleClasse'],
                level=lvl,
                students={}
            )
            self.by_sections[sect.id] = sect
            lvl.sections[sect.id] = sect

        return self

    def scrap_students(self):
        if not self.is_logged_in():
            print('Not logged in, logging in...')
            self.login()

        html = __sess__.get(STUDENTS_URL).text

        self.scrap_sections(html, check_login=False)

        sec: Section
        for sec in self.by_sections.values():
            html = __sess__.post(STUDENTS_API_URL, params={
                'TypeEnseignement': sec.level.education.id,
                'Cycle': sec.level.cycle.id,
                'Niveau': sec.level.id,
                'Classe': sec.id,
            }).text
            doc = bs(html, 'html.parser')

            _, rows = parse_table(doc)

            students_by_name = {}
            for opt in rows:
                student = Student(
                    id=opt[0],
                    name=opt[1],
                    image=None,
                    birthday=datetime.strptime(opt[2], '%d-%m-%Y' if '-' in opt[2] else '%d/%m/%Y'),
                    gender=opt[3],
                    section=sec,
                    grades={}
                )
                sec.students[opt[0]] = student
                self.by_students[student.id] = student
                students_by_name[student.name] = student

            profile: Tag
            for profile in doc.select('.col-lg-2.col-md-3'):
                name = profile.select_one('.box-footer').text.strip()
                student: Student = students_by_name[name]
                student.image = profile.select_one('img').get('src')

        self.scrap_subjects()

        sess: Session
        subj: Subject
        for sess in self.sessions.values():
            for subj in self.subjects.values():
                for lvl in subj.levels:
                    data = __sess__.post(FILTER_GRADES_API_URL, data={
                        'Niveau': lvl.id,
                        'Matiere': subj.id,
                    }).json()
                    for opt in data:
                        quiz = Quiz(
                            id=opt['Value'],
                            name=opt['Text'],
                        )
                        for sec in lvl.sections.values():
                            html = __sess__.post(GRADES_API_URL, data={
                                'TypeEnseignement': lvl.education.id,
                                'Cycle': lvl.cycle.id,
                                'Niveau': lvl.id,
                                'Classe': sec.id,
                                'Matiere': subj.id,
                                'IdSession': sess.id,
                                'IdControleContinu': quiz.id,
                                'EleveSansNotes': 'false',
                            }).text
                            doc = bs(html, 'html.parser')
                            _, rows = parse_table(doc)

                            for row in rows:
                                student = self.by_students[row[0]]
                                student.grades[subj, sess, quiz] = row[2]
                    

        return self
        
    