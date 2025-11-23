<?php
session_start();
require_once __DIR__ . "/../api/db.php";

if (!isset($_SESSION["admin_logged"]) || $_SESSION["admin_logged"] !== true) {
    header("Location: login.php");
    exit;
}

$db = mongo_db();

// ---- Fetch Counts ----
$users_count      = $db->users->countDocuments();
$videos_count     = $db->videos->countDocuments();
$cats_count       = $db->categories->countDocuments();
$channels_count   = $db->channels->countDocuments();
$tokens_count     = $db->tokens->countDocuments();
$force_sub_count  = $db->force_sub->countDocuments();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body {
            background: #121212;
            font-family: Arial, sans-serif;
            color: white;
            margin: 0;
            padding: 0;
        }
        .header {
            background: #1F1F1F;
            padding: 20px;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
        }
        .container {
            padding: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
        }
        .card {
            background: #1E1E1E;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }
        .card h2 {
            margin: 0;
            font-size: 40px;
            color: #00A8FF;
        }
        .card p {
            margin-top: 10px;
            font-size: 16px;
            color: #aaa;
        }
        .menu {
            margin-top: 40px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        .menu a {
            display: block;
            background: #0084ff;
            padding: 14px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            color: white;
            font-weight: bold;
        }
        .logout {
            margin-top: 35px;
            text-align: center;
        }
        .logout a {
            padding: 14px 20px;
            background: #FF4747;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
    </style>
</head>

<body>

<div class="header">Admin Dashboard</div>

<div class="container">

    <div class="grid">

        <div class="card">
            <h2><?= $users_count ?></h2>
            <p>Total Users</p>
        </div>

        <div class="card">
            <h2><?= $videos_count ?></h2>
            <p>Total Videos</p>
        </div>

        <div class="card">
            <h2><?= $cats_count ?></h2>
            <p>Categories</p>
        </div>

        <div class="card">
            <h2><?= $channels_count ?></h2>
            <p>Video Channels</p>
        </div>

        <div class="card">
            <h2><?= $force_sub_count ?></h2>
            <p>Force-Sub Channels</p>
        </div>

        <div class="card">
            <h2><?= $tokens_count ?></h2>
            <p>Tokens Generated</p>
        </div>

    </div>

    <div class="menu">
        <a href="videos.php">Manage Videos</a>
        <a href="add_video.php">Add New Video</a>
        <a href="categories.php">Manage Categories</a>
        <a href="channels.php">Manage Channels</a>
        <a href="settings.php">Settings</a>
        <a href="users.php">User Manager</a>
    </div>

    <div class="logout">
        <a href="logout.php">Logout</a>
    </div>

</div>

</body>
</html>

