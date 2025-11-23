<?php
session_start();
require_once __DIR__ . "/../api/db.php";

if (!isset($_SESSION["admin_logged"]) || $_SESSION["admin_logged"] !== true) {
    header("Location: login.php");
    exit;
}

$db = mongo_db();

// Fetch categories and channels
$categories = $db->categories->find();
$channels   = $db->channels->find();

$message = "";

// Handle video add
if ($_SERVER["REQUEST_METHOD"] === "POST") {

    $title    = trim($_POST["title"]);
    $category = trim($_POST["category"]);
    $channel  = trim($_POST["channel"]);
    $file_id  = trim($_POST["file_id"]);
    $price    = intval($_POST["price"]);

    if (!$title || !$category || !$channel || !$file_id || !$price) {
        $message = "All fields are required!";
    } else {
        try {
            $db->videos->insertOne([
                "title"    => $title,
                "category" => $category,
                "channel"  => $channel,
                "file_id"  => $file_id,
                "price"    => $price,
                "added"    => new MongoDB\BSON\UTCDateTime()
            ]);

            $message = "Video added successfully!";
        } catch (Exception $e) {
            $message = "Error: " . $e->getMessage();
        }
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Add New Video</title>
    <style>
        body {
            background: #121212;
            font-family: Arial, sans-serif;
            color: white;
        }
        .container {
            width: 550px;
            margin: 40px auto;
            background: #1e1e1e;
            padding: 30px;
            border-radius: 10px;
        }
        h2 {
            text-align: center;
        }
        label {
            display: block;
            margin-top: 15px;
            font-size: 15px;
            color: #aaa;
        }
        input, select {
            width: 100%;
            padding: 12px;
            margin-top: 5px;
            background: #2a2a2a;
            border: none;
            border-radius: 6px;
            color: white;
        }
        button {
            margin-top: 25px;
            width: 100%;
            padding: 14px;
            background: #0084ff;
            border: none;
            border-radius: 7px;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        .back {
            margin-top: 20px;
            text-align: center;
        }
        .back a {
            color: #00aaff;
            text-decoration: none;
        }
        .msg {
            text-align: center;
            margin-top: 10px;
            color: #00ff88;
        }
    </style>
</head>
<body>

<div class="container">

    <h2>Add New Video</h2>

    <?php if ($message): ?>
        <p class="msg"><?= $message ?></p>
    <?php endif; ?>

    <form method="POST">

        <label>Title:</label>
        <input type="text" name="title" required>

        <label>Category:</label>
        <select name="category" required>
            <option value="">Select Category</option>
            <?php foreach ($categories as $c): ?>
            <option value="<?= $c['key'] ?>"><?= $c['name'] ?></option>
            <?php endforeach; ?>
        </select>

        <label>Channel:</label>
        <select name="channel" required>
            <option value="">Select Channel</option>
            <?php foreach ($channels as $ch): ?>
            <option value="<?= $ch['name'] ?>"><?= $ch['name'] ?> (<?= $ch['channel_id'] ?>)</option>
            <?php endforeach; ?>
        </select>

        <label>Video file_id:</label>
        <input type="text" name="file_id" placeholder="Paste file_id" required>

        <label>Price (points):</label>
        <input type="number" name="price" required>

        <button type="submit">Add Video</button>

    </form>

    <div class="back">
        <a href="videos.php">← Back to Video List</a>
    </div>

</div>

</body>
</html>
