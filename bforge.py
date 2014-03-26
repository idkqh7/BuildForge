__version__ = '0.0.1.0'
__author__ = 'idkqh7'

__usage__ = 'MAIN COMMAND\n' \
    '----------------\n' \
    '%prog init     :   create cookbook\n' \
    '%prog install  :   install recipes by berkshelf\n' \
    '%prog remove   :   remove recipes\n' \
    '----------------\n'



import os
import shutil
from optparse import OptionParser

def replace_file_text(action_list, file):
    #fix Vagrantfile
    string = ""

    tmp = file + '.tmp'
    with open(file, encoding='utf-8') as f:
        string = f.read()


    for replace_tuple in action_list:
        old, new = replace_tuple
        try:
            string.index(old)
        except:
            print(old)
            raise

        string = string.replace(old, new)


    with open(tmp, mode='w', encoding='utf-8') as f:
        f.write(string)
    os.remove(file)
    os.rename(tmp, file)

def init(c_args):

    #try command 'berks cookbook'
    cookbook_dir = c_args[0]
    try:
        os.system('berks cookbook ' + cookbook_dir)
    except Exception as e:
        print('Error:' + e.message)
        return

    #disable vagrant-berkshelf
    replace_list = [('# config.berkshelf', 'config.berkshelf'),
                    ('config.berkshelf', '# config.berkshelf')]
    replace_file_text(replace_list, cookbook_dir + '/Vagrantfile')

    print("SUCCEED!")

def remove(recipes):
    #remove recipes on Berksfile
    for recipe in recipes:
        replace_list = [("\n" + "cookbook '" + recipe + "'", '')]
    replace_file_text(replace_list, 'Berksfile')

    #remove recipes on Vagrantfile
    for recipe in recipes:
        replace_list = [('\n        "recipe['+ recipe +']",', '')]
    replace_file_text(replace_list, 'Vagrantfile')

    print("SUCCEED!")



def install(recipes):

    if not os.path.exists('Berksfile'):
        print('ERROR : Berksfile does not exist')
        return

    if not os.path.exists('Vagrantfile'):
        print('ERROR : Vagrantfile does not exist')
        return


    print("recipe list : ", recipes)

    new_recipes = []

    #pass already writing recipes
    with open('Berksfile', encoding='utf-8') as berks:
        string = berks.read()
        for recipe in recipes:
            if not "cookbook '" + recipe + "'" in string:
                new_recipes.append(recipe)

    #add recipes
    with open('Berksfile', mode='a', encoding='utf-8') as berks:
        for recipe in new_recipes:
            berks.write("\n" + "cookbook '" + recipe + "'")

    # #add chef.run_list
    old = 'chef.run_list = ['
    new = old
    for recipe in new_recipes:
        new += '\n        "recipe['+ recipe +']",'
    replace_list = [(old, new)]
    replace_file_text(replace_list, 'Vagrantfile')

    # if os.path.isfile("Berksfile.lock"):
    #     os.remove("Berksfile.lock")
    if os.path.isdir('cookbooks'):
        shutil.rmtree('cookbooks')
    os.system("berks vendor cookbooks")

    print("SUCCEED!")



if __name__ == '__main__':


    #get option & arguments
    p = OptionParser(usage=__usage__, version="bforge version {0}".format(__version__))
    options, args = p.parse_args()

    #switch mode
    c = args[0]
    c_args = args[1:]

    #remove duplication
    c_args = list(set(c_args))

    if len(args) < 0:
        print("more infomation 'help' ")
    elif c == "init":
        init(c_args)
    elif c == "install":
        install(c_args)
    elif c == "remove":
        remove(c_args)
    else:
        print("ERROR:invalid command")