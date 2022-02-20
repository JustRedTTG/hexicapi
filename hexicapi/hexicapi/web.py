from hexicapi.verinfo import __version__, __title__, __author__, __license__, __copyright__
import os,socket,base64,time,requests
from bottle import route,run,post,request,response,static_file
allowGuest=False
class action:
    def auth(username,password):
        if os.path.exists("users/"+username):
            with open("users/"+username+"/auth") as f:
                f.seek(0)
                if f.read()==password:
                    return True, False
                else:
                    return False,allowGuest
        else:
            if username!="":
                return allowGuest,allowGuest
            else:
                return False,False
    def idname(id):
        with open("users/"+str(id)) as f:
            name = str(f.read())
        return name
    def nameid(name):
        with open("users/"+str(name)+"/id") as f:
            id = int(f.read())
        return id
def redirect(link):
    return '<meta http-equiv="refresh" content="0; URL='+link+'" />'
def header(margin="10%"):
    return """<style>html {font-family: 'Brush Script MT', cursive;} body {margin:0;padding:0;} .nomargin {margin:0;} .ilnomargin {margin:0;display:inline;}</style>
    <header style="background-color:#101010;color:#FFFFFF;margin-bottom:"""+str(margin)+""";;padding:5;">
    <h1 class="ilnomargin">Maseic</h1>
    <p class="ilnomargin">a web service made by Red</p>
    </header>"""
def readHTML(file):
    return static_file(file, root=os.path.dirname(os.path.realpath(__file__)))
def mainPage():
    r = requests.get('https://hexicapi.free.bg/')
    return r.text
def RUN(host,port,serv=True,page=mainPage):
    if not os.path.exists('users'):
        os.mkdir('users')
    @route("/authpage/<file:path>")
    def authpage(file):
        return readHTML('authpage/'+file)
    @route("/script/<script>")
    def get_script(script):
        if os.path.exists("scripts/"+script):
            with open("scripts/"+script) as f:
                return f.read()
        else:
            return 'window.location.replace("http://maseic.strangled.net");'
    @route("/image/<image>")
    def get_image(image):
        if os.path.exists("images/"+image):
            return static_file(image,"images/")
        else:
            return ""
    @route("/")
    def main():
        return page()
    @route("/login/check")
    def check():
        auth = request.get_cookie("auth")
        if auth=="True":
            auth=True
        else:
            auth=False
        username = request.get_cookie("username")
        if username==None:
            username="NOAUTH"
        password = request.get_cookie("password")
        if password==None:
            password="Tk9BVVRI"
        password=password.encode("utf-8")
        password = base64.b64decode(password).decode()
        if os.path.exists("users/"+username):
            with open("users/"+username+"/auth") as f:
                if auth and password==f.read():
                    auth=True
                else:
                    auth=False
        if auth:
            return "yes:"+username+"\n"+redirect("/")
        else:
            return "no:Guest\n"+redirect("/login")
    @route("/login")
    def login():
        return readHTML('authpage/login.html')
    @route("/register")
    def register():
        return readHTML('authpage/register.html')
    @post('/login/proccess')
    def do_login():
        username = request.forms.get('username')
        password = request.forms.get('pass')
        auth = action.auth(username,password)[0]
        if auth:
            response.set_cookie("auth","True")
        else:
            response.set_cookie("auth","False")
        response.set_cookie("username",username)
        epas=base64.b64encode(bytes(password.encode("utf-8")))
        response.set_cookie("password",epas.decode("utf-8"))
        if not auth:
            return redirect("/login?fail=yes")
        else:
            return redirect("/")
    @post('/register/proccess')
    def do_register():
        username = request.forms.get('username')
        password = request.forms.get('pass')
        #print("register",username,password)
        if username=="":
          return redirect("/register?fail=yes")
        if password=="":
          return redirect("/register?fail=yes")
        if os.path.exists("users/"+username):
            auth = action.auth(username,"")[0]
        else:
            #print("make")
            os.mkdir("users/"+username)
            with open("users/"+username+"/id","a+") as f:
                id=0
                while os.path.exists("users/"+str(id)):
                    id+=1
                f.write(str(id))
            with open("users/" + username + "/auth", "a+") as f:
                f.write(password)
            with open("users/"+str(id),"a+") as f:
                f.write(username)
            auth = action.auth(username, password)[0]
        if auth:
            response.set_cookie("auth","True")
        else:
            response.set_cookie("auth","False")
        response.set_cookie("username",username)
        epas=base64.b64encode(bytes(password.encode("utf-8")))
        response.set_cookie("password",epas.decode("utf-8"))
        if not auth:
            return redirect("/register?fail=yes")
        else:
            return redirect("/")
    print("running webserver")
    try:
      run(host=host,port=port,quiet=serv,reloader=not serv)#,server='gunicorn',keyfile='key.pem',certfile='cert.pem')
    except:
      print("an error occured")
    print("what happened here, looks like it stopped...")


if __name__ == '__main__':
    print('RUN("localhost",80,True,mainPage)')
