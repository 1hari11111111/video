<?php
session_start();
require_once __DIR__ . "/../api/db.php";

// -------------------------------------------------------------
// ADMIN CREDENTIALS (you set these)
// -------------------------------------------------------------
$ADMIN_USERNAME = "hari813";
$ADMIN_PASSWORD = "hari813142";

// -------------------------------------------------------------
// IF ALREADY LOGGED IN → REDIRECT
// -------------------------------------------------------------
if (isset($_SESSION["admin_logged"]) && $_SESSION["admin_logged"] === true) {
    header("Location: dashboard.php");
    exit;
}

// -------------------------------------------------------------
// HANDLE LOGIN SUBMISSION
// -------------------------------------------------------------
$error = "";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $user = trim($_POST["username"]);
    $pass = trim($_POST["password"]);

    if ($user === $ADMIN_USERNAME && $pass === $ADMIN_PASSWORD) {
        $_SESSION["admin_logged"] = true;
        header("Location: dashboard.php");
        exit;
    } else {
        $error = "Invalid username or password!";
    }
}

?>
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body {
            background: #111;
            color: #fff;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .box {
            background: #1e1e1e;
            padding: 30px 40px;
            border-radius: 10px;
            width: 350px;
            text-align: center;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            border: none;
            background: #333;
            color: #fff;
            font-size: 15px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #0084ff;
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        .error {
            color: #ff4747;
            margin-bottom: 10px;
        }
        h2 {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>

<div class="box">
    <h2>Admin Login</h2>

    <?php if ($error): ?>
    <div class="error"><?= $error ?></div>
    <?php endif; ?>

    <form method="POST">
        <input type="text" name="username" placeholder="Username" required autofocus>
        <input type="password" name="password" placeholder="Password" required>
        <button>Login</button>
    </form>
</div>

</body>
</html>
