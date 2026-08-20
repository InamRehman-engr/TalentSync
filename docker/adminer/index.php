<?php
function adminer_object() {
    class AdminerCustomLogin extends Adminer {
        function login($login, $password) {
            // Let the database engine validate credentials
            return true;
        }
        function serverName($server) {
            return 'NHR Database';
        }
    }
    return new AdminerCustomLogin;
}

// Force the server to the Docker service name so users can't misconfigure it
if (empty($_GET['server']) && empty($_POST['auth']['server'])) {
    $_GET['server'] = 'db';
}

include './adminer.php';
