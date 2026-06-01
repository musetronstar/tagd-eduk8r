# twitter-clone-tutorial

LAMP Stack Tutorial building a simple twitter clone.

We follow the [TechLead tutorial](https://www.youtube.com/watch?v=1YXqXPWjmKk)

This is a meant for learning purposes, not for production use!
Use at your own risk.

We performed this tutorial as part of a classroom project.
Some of the instructions are specific to the configuration of our
servers in our classroom.

If you are a member of the public, your configuration is most
likely different.

## Setup

TechLead is using an older version CentOS + Apache where we are using the
latest Ubuntu Server + Nginx. He is using an ancient version of php (v5.4.18),
where we are using v8.0.8, so the older MySQL Native Driver (mysqlnd)
functions will not work.

Numbers in brackets with colons indicate timestamps in the video. For example,
when TechLead talks about the tech stack: [4:18]

We do not copy TechLead when he registers a domain name [0:20] and
purchases hosting [1:15]. Instead we use our VM development server
and hostname.

Also, we do not copy when he installs Apache [4:49], PHP [5:48]
and MariaDB [6:28]. We already have NginX, PHP and MariaDB installed.

## Steps

1. Log in to github.com and create a repository. Clone it.

    ```bash
    # on your ICT computer
    cd ~/var
    # replace <github user> with yours
    git clone git@github.com:<github user>/twitter-clone-tutorial.git
    cd twitter-clone-tutorial
    # create the document root
    mkdir www
    ```

2. Configure your webserver to use the repository you created.

    * Log in to your development server: `ssh dev`
    * Disable your currently configured websites

    ```bash
    cd /etc/nginx/
    sudo unlink sites-enabled/student.conf
    ```

    * Configure tutorial site

    ```bash
    sudo cp sites-available/students.conf sites-available/twitter-tutorial.conf
    ```

    ```conf
    # replace the document root with:
    root /home/dev/var/twitter-clone-tutorial/www;
    ```

    * Enable tutorial site

    ```bash
    sudo ln -s sites-available/twitter-tutorial.conf sites-enabled/
    sudo nginx -t  # make sure no errors
    sudo nginx -s reload
    ```

4. Test php in your document root [6:16]

    ```bash
    cd ~/var/twitter-clone-tutorial
    vi www/index.php
    ```

    ```php
    <?php phpinfo() ?>
    ```

    Go to `http://your-dev-vm-hostname` in your browser.

    If there are errors
    * Enable debugging and reload. Debug the error.
    * It can also be helpful to watch the web server logs.

    ```bash
    sudo tail -f /var/log/nginx/*.log
    ```

3. Do not copy TechLead when he creates the database [7:53],
   users table [6:55] or a user [7:55].

   Instead, create a file `tweetlead-init.sql` to contain the
   following SQL statments.

    ```sql
    DROP DATABASE IF EXISTS tweetlead;
    CREATE DATABASE tweetlead;

    DROP USER IF EXISTS tweetuser@localhost;
    CREATE USER tweetuser@localhost IDENTIFIED BY 'tweet123';
    GRANT ALL PRIVILEGES ON tweetlead.* TO tweetuser@localhost;

    use tweetlead;

    CREATE TABLE users (
      uid int auto_increment,
      primary key(uid),
      ip varchar(64) unique
    );

    CREATE TABLE tweets (
      tid int auto_increment,
      primary key(tid),
      uid int,
      post varchar(140),
      date datetime,
      key(date),
      key(tid, date)
    );

    CREATE TABLE follows (
      uid int,
      follower int,
      primary key(uid, follower)
    );
    ```

    * Execute the SQL file on your dev server to create the tables.

    ```bash
    sudo mysql < tweetlead-init.sql
    ```

4. Insert database test data using a file.
    * create a file `tweetlead-test-data.sql`

    ```sql
    use tweetlead;

    INSERT INTO users(ip) VALUES ('1.2.3.4');
    INSERT INTO users(ip) VALUES ('2.3.4.5');
    INSERT INTO users(ip) VALUES ('3.4.5.6');

    INSERT INTO tweets(uid, post, date)
    VALUES (
      (SELECT uid FROM users WHERE ip = '1.2.3.4'),
      'Check out my simple twitter clone',
      NOW() - INTERVAL 1 WEEK
    );

    INSERT INTO tweets(uid, post, date)
    VALUES (
      (SELECT uid FROM users WHERE ip = '2.3.4.5'),
      'TweetLead is so fast!',
      NOW() - INTERVAL 1 day
    );

    INSERT INTO tweets(uid, post, date)
    VALUES (
      (SELECT uid FROM users WHERE ip = '3.4.5.6'),
      'Some day I will be as good as TechLead!!!',
      NOW()
    );
    ```

* Execute the SQL file on your dev server.

    ```bash
    sudo mysql < tweetlead-test-data.sql
    ```

5. Edit `www/index.php` and create database connection.
   Note the `DEBUG` code is not present in TechLead's.
   PHP does not print errors by default for security reasons.
   Setting `DEBUG` to `1` enables error printing and debug
   statements, but should be disabled in production code.
   Watching the web server logs is also a way to debug.

    ```php
    <?php
    /*
     * DEBUG 1 = show errors when they occur
     * DEBUG 0 = disable error reporting
     */
    define('DEBUG', 0);
    if (DEBUG) {
      ini_set('display_errors', '1');
      ini_set('display_startup_errors', '1');
      error_reporting(E_ALL);
    }

    $dbhost = 'localhost';
    $dbname = 'tweetlead';
    $dbuser = 'tweetuser';
    $dbpass = 'tweet123';
    $conn = mysqli_connect($dbhost, $dbuser, $dbpass);
    mysqli_select_db($conn, $dbname);

    $result = mysqli_query($conn, "SELECT * FROM users");
    while ($row = mysqli_fetch_row($result)) {
      print_r($row);
    }
    ?>
    ```

* Test the file by executing CLI php

    ```bash
    php www/index.php
    ```

    You should see output for the users we created
6. [8:24] Remove test query and while loop. Define the `query()` function.

    ```php
    function query($query) {
      $result = mysqli_query($GLOBALS['conn'], $query);
      if (DEBUG) {
        echo $query, "<br>";
        if (!$result) {
          echo "<br>", mysqli_error($GLOBALS['conn']);
        }
      }
      return $result;
    }
    ```

7. [10:26] Create HTML form. The code between the `<<<EOF ... EOF` is a *heredoc* string.

    ```php
    print <<<EOF

    <form action="index.php">
      <textarea name="tweet"></textarea>
      <input type="submit" value="Tweet">
    </form>

    EOF;
    ```

8. [10:45] Print the tweet and IP address of the "logged in" user.

    ```php
    if (isset($_REQUEST['tweet'])) {
      $tweet = $_REQUEST['tweet'];
      $ip = $_SERVER['REMOTE_ADDR'];
      print "$tweet, $ip";
    }
    ```

9. [11:11] Create the "logged in" user if does not exists.
   Replace the previous snippet with this.

    ```php
    function get_single($query) {
      $result = query($query);
      $row = mysqli_fetch_row($result);
      return $row[0];
    }

    if (isset($_REQUEST['tweet'])) {
      $tweet = mysqli_real_escape_string($conn, $_REQUEST['tweet']);
      $ip = mysqli_real_escape_string($conn, $_SERVER['REMOTE_ADDR']);

      $uid = get_single("SELECT uid FROM users WHERE ip = '".$ip."'");
      if (!$uid) {
        query("INSERT INTO users(ip) VALUES ('$ip')");
      }

      print "$tweet, $ip";
    }
    ```

10. [12:18] Insert tweet

    ```php
    $date = Date("Y-m-d H:i:s");
    query("INSERT INTO tweets(uid, post, date) VALUES ('$uid', '$tweet', '$date')");
    ```

11. [12:51] Output Tweets

    ```php
    $result = query("SELECT * FROM tweets ORDER BY date DESC");
    print '<table border="1">';
    while ($row = mysqli_fetch_assoc($result)) {
      $user = get_uid();
      $uid = $row['uid'];
      $post = htmlspecialchars($row['post']);
      $date = $row['date'];

      if (!get_single("SELECT follower FROM follows WHERE uid=$user AND follower=$uid")) {
        $follow = "<a href=\"index.php?follow=$uid\">Follow</a>";
      } else {
        $follow = "Followed";
      }
      print <<<EOF
      <tr>
        <td>$uid</td>
        <td>$post</td>
        <td>$date</td>
        <td>$follow</td>
      </tr>
    EOF;
    }
    print "</table>";
    ```

12. [14:09]  Handle follows

    ```php
    function get_uid() {
      $ip = mysqli_real_escape_string($GLOBALS['conn'], $_SERVER['REMOTE_ADDR']);
      $uid = get_single("SELECT uid FROM users WHERE ip = '".$ip."'");
      if (!$uid) {
        query("INSERT INTO users(ip) VALUES ('$ip')");
      }
      return $uid;
    }

    if (isset($_REQUEST['follow'])) {
      $follow = mysqli_real_escape_string($GLOBALS['conn'], $_REQUEST['follow']);
      $uid = get_uid();
      // ignore errors, such as duplicate entries that violate the primary key
      query("INSERT IGNORE INTO follows(uid, follower) VALUES ('$uid', '$follow')");
    }
    ```

13. [15:11] Section for followed users

    ```php
    print "<hr>";

    print "Followed users";
    ```

14. [15:17] Render tweets function. Put the code that prints a table of tweets into a function.

    ```php
    function render_tweets($tweets) {
      print '<table border="1">';
      foreach ($tweets as $tweet) {
        $user = get_uid();
        $uid = $tweet['uid'];
        $post = htmlspecialchars($tweet['post']);
        $date = $tweet['date'];

        if (!get_single("SELECT follower FROM follows WHERE uid=$user AND follower=$uid")) {
                $follow = "<a href=\"index.php?follow=$uid\">Follow</a>";
        } else {
          $follow = "Followed";
        }
        print <<<EOF
        <tr>
          <td>$uid</td>
          <td>$post</td>
          <td>$date</td>
          <td>$follow</td>
        </tr>
            EOF;
        }
      print "</table>";
    }
    ```

14. [15:26] Modify the while loop to fill an array of tweets and call the render tweets function.

    ```php
    $result = query("SELECT * FROM tweets ORDER BY date DESC");
    $tweets = array();
    while ($row = mysqli_fetch_assoc($result)) {
      $tweets[] = $row;
    }
    render_tweets($tweets);
    ```

15. [15:28] Copy the "all" tweets code and modify for followed users

    ```php
    $user = get_uid();
    $tweets = array();
    $result = query("SELECT * FROM tweets WHERE uid IN (SELECT follower FROM follows WHERE uid=$user) ORDER BY date DESC");
    while ($row = mysqli_fetch_assoc($result)) {
      $tweets[] = $row;
    }
    render_tweets($tweets);
    ```

16. [15:54] Add bootstrap CSS style. Replace the entire form *heredoc* string with this

    ```php
    print <<<EOF
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
    <style>
    body {
      padding: 20px;
    }
    </style>

    <form action="index.php">
      <table><tr>
        <td>
          <textarea name="tweet" class="form-control" aria-label="With textarea"></textarea>
        </td>
        <td>
          <button type="submit" value="Tweet" class="btn btn-primary">Tweet</button>
        </td>
      </tr>
    </form>

    EOF;
    ```
17. [16:51] Add unfollow feature. Replace

    ```php
    $follow = "Followed";
    ```

    With

    ```php
    $follow = "<a href=\"index.php?unfollow=$uid\">Unfollow</a>";
    ```

    Delete the entry from the `follows` table

    ```php
    if (isset($_REQUEST['unfollow'])) {
      $unfollow = mysqli_real_escape_string($GLOBALS['conn'], $_REQUEST['unfollow']);
      $uid = get_uid();
      query("DELETE FROM follows WHERE uid='$uid' AND follower='$unfollow'");
    }
    ```

That's all for the tutorial. Now, clean it up and see how you can improve upon it.

Thank you TechLead for the excellent tutorial!
