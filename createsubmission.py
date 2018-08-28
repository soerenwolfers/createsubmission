#! /usr/bin/env python3
import sys
import os
import shutil
import re
from swutil.files import find_files,zip_dir,read_pdf
from pathlib import Path
import argparse
import tempfile
import subprocess
import textwrap
HOME=str(Path.home())
TEXMF=os.path.join(HOME,'texmf')
TEX_PACKAGES=os.path.join(TEXMF,'tex','latex')
TEX_LIBRARIES = os.path.join(TEXMF,'bibtex','bib','base')
AUXILIARY_FILEENDINGS=['log','aux','dvi','lof','lot','bit','idx','glo','bbl','bcf','ilg','toc','ind','out','blg','fdb_latexmk','fls','upa','upb','synctex.gz']
FORBIDDEN_PATTERNS = {'??':'broken references','[\n?\n]':'broken citations'}
def copy_to_matching_tex(src_path,target_path,pattern):
    re_pattern = re.compile(pattern)
    for file_path in find_files('*.tex',target_path,match_name=True):
        with open(file_path,'r') as file:
            for line in file.readlines():
                if re_pattern.search(line):
                    break
            else:
                continue
            if not os.path.isfile(os.path.join(os.path.dirname(file_path),os.path.basename(src_path))):
                shutil.copy(src_path,os.path.dirname(file_path))

def create_submission(fromm,to,bibliography='library.bib'):
    if fromm[-1] ==os.sep:
        fromm=fromm[:-1]
    if to[-4:]!='.zip':
        zip_path = to+'.zip'
    print(f'I am going to create {zip_path} with all files from {fromm}')
    with tempfile.TemporaryDirectory() as tmpdir:#now that the desired zip path has been created, the target can be replaced by temporary directory'
        to = os.path.join(tmpdir,'submission')#mkdtemp creates 
        #the directory but copytree below also tries to make the directory that is passed 
        # to it and fails if it already exists
        if os.path.exists(zip_path):
            print(f'Error: {zip_path} already exists')
            sys.exit(1)
        errors = {}
        shutil.copytree(fromm,to)
        packages = os.listdir(TEX_PACKAGES)
        for package in packages:
            copy_to_matching_tex(os.path.join(TEX_PACKAGES,package,package+'.sty'),to,r'\\(usepackage|requirepackage)(\[.*?\])?\{(.*?,)*'+package+r'(,.*?)*?\}')
        bibfiles = find_files(bibliography,TEX_LIBRARIES,match_name=True)
        for bibfile in bibfiles:
            copy_to_matching_tex(bibfile,to,pattern=r'\\documentclass')#need double backslash because escaping happens down the line again
        for file_path in find_files('*.tex',to):
            with open(file_path,'r') as file:
                for line in file.readlines():
                    if 'begin{document}' in line:
                        break
                else:
                    continue
                print(f'I am going to compile {os.path.relpath(file_path,to)}')
                owd = os.getcwd()
                os.chdir(os.path.dirname(file_path))
                try:
                    subprocess.run(['pdflatex','--interaction=nonstopmode',os.path.basename(file_path)])
                    subprocess.run(['bibtex',os.path.basename(file_path)])
                    subprocess.run(['pdflatex','--interaction=nonstopmode',os.path.basename(file_path)])
                    subprocess.run(['pdflatex','--interaction=nonstopmode',os.path.basename(file_path)])
                except exception:
                    cont = input(f'Error during compilation. Continue?')
                    if cont not in ['y','Y']:
                        sys.exit()
                os.chdir(owd)
        for file_path in find_files('*.pdf',to):#check for missing references etc
            txt = read_pdf(file_path,split_pages = True)
            matches = {pattern:[i for (i,page) in enumerate(txt) if pattern in page]
                    for pattern in FORBIDDEN_PATTERNS} 
            matches ={pattern:matches[pattern] for pattern in matches if matches[pattern]}
            if matches:
                errors[file_path] = matches
        if errors:
            [print(f'File {file} seems to contain {FORBIDDEN_PATTERNS[pattern]} on '
            f'page{"s" if len(errors[file][pattern])>1 else ""} {", ".join(str(i+1) for i in errors[file][pattern])}') for file
            in errors for pattern in errors[file]]
            cont = input('Continue? (y/n)')
            if cont not in ['y','Y']:
                sys.exit()
        delete = [ file for ending in AUXILIARY_FILEENDINGS for file in find_files('*.'+ending,to)]
        for file in delete:
            os.remove(file)
        zip_dir(zip_path,to,rename_source_dir = os.path.basename(fromm))
        print(f'Successfully created {zip_path}')

if __name__=='__main__':
    class LineWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _split_lines(self, text, width):
            text = self._whitespace_matcher.sub(' ', text).strip()
            return textwrap.wrap(text, width)
    parser=argparse.ArgumentParser(formatter_class=LineWrapRawTextHelpFormatter,
        description = textwrap.dedent('''\
                Create zip file from latex repository.
                
                - include all necessary packages from local tex tree
                - include bib files from local tex tree
                - remove unnecessary auxiliary files
                - check all citations and references 
                '''
    ))
    parser.add_argument('source',action='store',help='Source directory')
    parser.add_argument('target',action='store',help='Target file')
    args=parser.parse_args()
    create_submission(args.source,args.target)
