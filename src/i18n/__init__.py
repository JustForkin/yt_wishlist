import gettext
import glob
import os

def setup_get_text(src_dir, lang_dir, domain_name, language):
    if '_' in __builtins__:
        return

    # scan source tree and generate translation template file
    pot_file = os.path.join(lang_dir, domain_name + '.pot')
    generate_po_template(src_dir, pot_file)

    # update translation files (.po and .mo files)
    compile_mo_recursively(lang_dir, pot_file)

    # setup the underscore function
    translation = gettext.translation(domain_name, localedir=lang_dir, languages=[language])
    translation.install()

def generate_po_template(src_dir, output_file):
    '''
        See: https://stackoverflow.com/questions/739314/easiest-way-to-generate-localization-files
    '''
    filenames = list_files_recursively(src_dir, '.py')

    print('Generate translation template: {0}'.format(output_file))

    cmd = 'xgettext --output {0} {1}'.format(output_file, ' '.join(filenames))
    os.system(cmd)

def compile_mo_recursively(lang_dir, pot_file):
    for po_file in list_files_recursively(lang_dir, '.po'):
        mo_file = po_file[:-3] + '.mo'

        print('Merge existing strings with the new template: {0}'.format(po_file))

        cmd = 'msgmerge --update {0} {1} --no-location --sort-output'.format(po_file, pot_file)
        os.system(cmd)

        print('Compile binary translation: {0}'.format(mo_file))

        cmd = 'msgfmt {0} --output-file {1}'.format(po_file, mo_file)
        os.system(cmd)

def list_files_recursively(path, ext):
    ''' compatible with Python 2 & 3 '''
    from os.path import join, splitext
    results = []
    for root, _subdirs, files in os.walk(path):
        results += [join(root, f) for f in files if splitext(f)[1] == ext]
    return results
