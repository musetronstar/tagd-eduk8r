# Login and Setup Your students.eduk8.us Linux Account

The first time you login to the `students.eduk8.us` Linux webserver, you will need to follow these steps:

## Use the console

Open a Windows command console.
* Press the `Win+R` key
* Type the `cmd` command and press enter

That should have launched a window with a console that allows you to enter commands manually - not using the *GUI*.

```console
C:\Users\Administrator>
```

On windows, the *prompt* line starts with a drive letter (e.g. `C:`, pronounced "C drive")
and ends with `>` (pronounced "greater than"), and perhaps a blinking cursor `_`.  That is where you enter commands.

When I say "enter a command," I mean type the command as written, and press `Enter`.

Enter the command `ping students.eduk8.us`. You should see the following in your console (if not, see the ICT teacher).

```bash
C:\Users\Administrator>ping students.eduk8.us

Pinging students.eduk8.us [192.168.10.13] with 32 bytes of data:
Reply from 192.168.10.13: bytes=32 time=1ms TTL=63
Reply from 192.168.10.13: bytes=32 time=2ms TTL=63
Reply from 192.168.10.13: bytes=32 time<1ms TTL=63
Reply from 192.168.10.13: bytes=32 time<1ms TTL=63

Ping statistics for 192.168.10.13:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 2ms, Average = 0ms
```

You just used the `ping` command to test connectivity between your local host and the `students.eduk8.us` host.  Based on this
output, what IP address is assigned to the `students.eduk8.us` host?

## Login using SSH

The most common and secure way to login to a Linux host over a network is using *SSH*.  Windows 10 has an *ssh client*,
but on older version of Windows you will need to use an ssh client called *PuTTy* (it is also installed on the ICT Lab
computers).

Enter the following command. The user will be the user name from your `eduk8.us` email address.
For example, mine is `isaac@eduk8.us`, so my students.eduk8.us user name is `isaac`.
* Enter `ssh <user>@students.eduk8.us`.
* Answer 'yes' to add students.eduk8.us to your list of known hosts (this is used to authenticate that students.eduk8.us is who it says it is).
* Your default password is `abc123`

```bash
C:\Users\Administrator>ssh isaac@students.eduk8.us
The authenticity of host 'students.eduk8.us (192.168.10.13)' can't be established.
ECDSA key fingerprint is SHA256:fEv/vrYGsMRl/j5re06IwQ8fZDjR6F9oblYrly9ijd8.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'students.eduk8.us,192.168.10.13' (ECDSA) to the list of known hosts.
isaac@students.eduk8.us's password:
            __          __  _
            \ \        / / | |
             \ \  /\  / /__| | ___ ___  _ __ ___   ___
              \ \/  \/ / _ \ |/ __/ _ \| '_ ` _ \ / _ \
               \  /\  /  __/ | (_| (_) | | | | | |  __/
                \/  \/ \___|_|\___\___/|_| |_| |_|\___|


     /$$                           /$$
    | $$                          | $$
    | $$$$$$$   /$$$$$$   /$$$$$$$| $$   /$$  /$$$$$$   /$$$$$$  /$$$$$$$$
    | $$__  $$ |____  $$ /$$_____/| $$  /$$/ /$$__  $$ /$$__  $$|____ /$$/
    | $$  \ $$  /$$$$$$$| $$      | $$$$$$/ | $$$$$$$$| $$  \__/   /$$$$/
    | $$  | $$ /$$__  $$| $$      | $$_  $$ | $$_____/| $$        /$$__/
    | $$  | $$|  $$$$$$$|  $$$$$$$| $$ \  $$|  $$$$$$$| $$       /$$$$$$$$
    |__/  |__/ \_______/ \_______/|__/  \__/ \_______/|__/      |________/


Last login: Wed Aug 21 15:42:57 2019 from 192.168.10.11
isaac@eduk8.us:~$
`
```

Change your password using the `passwd` command:

```bash
isaac@eduk8.us:~$ passwd
Changing password for isaac.
Current password:
New password:
Retype new password:
passwd: password updated successfully
```

## Create your user directory

* Make your webserver user directory: `mkdir www`
* Change into that directory: `cd www`.
* Print your working directory: `pwd`

```bash
isaac@eduk8.us:~$ mkdir www
isaac@eduk8.us:~$ cd www
isaac@eduk8.us:~/www$ pwd
/home/isaac/www
```

The *Apache* webserver uses a directive called `UserDir` to associate a URL path ending with
a "tilde username" to a subdirectory in the users home directory.  For example:

```
# index.html is the default
http://students.eduk8.us/~isaac/               ===>  /home/isaac/www/index.html
http://students.eduk8.us/~isaac/somefile.html  ===>  /home/isaac/www/somefile.html
```

## Create and test your home page

Create a temporary homepage: `echo "<html><body><h1>My Home Page</h1></body></html>" > index.html`

Check the contents of that file: `cat index.html`

```bash
isaac@eduk8.us:~/www$ echo "<html><body><h1>My Home Page</h1></body></html>" > index.html
isaac@eduk8.us:~/www$ cat index.html
<html><body><h1>My Home Page</h1></body></html>
```
Now open your web browser and go to `http://students.eduk8.us/~isaac/`. You should see "My Home Page".

You can also test it on the command line and see the entire HTTP response
using: `curl -D - http://students.eduk8.us/~isaac/`

```bash
isaac@eduk8.us:~/www$ curl -D - http://students.eduk8.us/~isaac/
HTTP/1.1 200 OK
Date: Thu, 22 Aug 2019 09:57:13 GMT
Server: Apache/2.4.38 (Ubuntu)
Last-Modified: Thu, 22 Aug 2019 09:46:22 GMT
ETag: "30-590b18ffc8849"
Accept-Ranges: bytes
Content-Length: 48
Content-Type: text/html

<html><body><h1>My Home Page</h1></body></html>
```
You are now ready to upload your website files. That's all for now.

You can exit the terminal by pressing `^D` or entering the `exit` command.

```bash
ict@eduk8.us:~$ cowsay -f tux "Happy Hacking!"
 ________________
< Happy Hacking! >
 ----------------
   \
    \
        .--.
       |o_o |
       |:_/ |
      //   \ \
     (|     | )
    /'\_   _/`\
    \___)=(___/
```
