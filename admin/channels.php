<?php
session_start();
require_once __DIR__ . "/../api/db.php";

if (!isset($_SESSION["admin_logged"]) || $_SESSION["admin_logged"] !== true) {
    header("Location: login.php");
    exit;
}

$db = mongo_db();
$message = "";

// --------------------- ADD CHANNEL -------------------------
if (isset($_POST["add"])) {
    $name = trim($_POST["name"]);
    $channel_id = trim($_POST["channel_id"]);

    if ($name && $channel_id) {
        try {
            $db->channels->updateOne(
                ["name" => $name],
                ['$set' => ["name" => $name, "channel_id" => intval($channel_id)]],
                ["upsert" => true]
            );
            $message = "Channel added successfully!";
        } catch (Exception $e) {
            $message = "Error: " . $e->getMessage();
        }
    }
}

// --------------------- DELETE CHANNEL -------------------------
if (isset($_GET["delete"])) {
    $name = $_GET["delete"];
    $db->channels->deleteOne(["name" => $name]);
    header("Location: channels.php");
    exit;
}

$channels = $db->channels->find();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Manage Channels</title>
    <style>
        body { background: #121212; color: white; font-family: Arial; }
        .container { width: 650px; margin: 40px auto; background: #1e1e1e; padding: 30px; border-radius: 10px; }
        label { display: block; margin-top: 15px; color: #bbb; }
        input { width: 100%; padding: 12px; margin-top: 5px; background: #2a2a2a; color: white; border-radius: 6px; border: none; }
        button { margin-top: 20px; width: 100%; padding: 14px; background: #0084ff; border: none; color: white; border-radius: 7px; }
        table { width: 100%; margin-top: 25px; border-collapse: collapse; }
        th, td { padding: 12px; border-bottom: 1px solid #333; }
        th { background: #222; }
        a { color: #00aaff; text-decoration: none; }
        .delete-btn { color: #ff4747 !important; }
        .msg { text-align: center; margin-top: 10px; color: #0f0; }
    </style>
</head>
<body>
<div class="container">

    <h2>Manage Video Channels</h2>

    <?php if ($message): ?>
        <p class="msg"><?= $message ?></p>
    <?php endif; ?>

    <form method="POST">
        <label>Channel Name (short name):</label>
        <input type="text" name="name" required>

        <label>Telegram Channel ID (numeric):</label>
        <input type="number" name="channel_id" required>

        <button type="submit" name="add">Add Channel</button>
    </form>

    <h3 style="margin-top:30px;">Registered Channels</h3>

    <table>
        <tr>
            <th>Name</th>
            <th>Channel ID</th>
            <th>Action</th>
        </tr>

        <?php foreach ($channels as $c): ?>
        <tr>
            <td><?= $c["name"] ?></td>
            <td><?= $c["channel_id"] ?></td>
            <td><a href="channels.php?delete=<?= $c['name'] ?>" class="delete-btn" onclick="return confirm('Delete this channel?')">Delete</a></td>
        </tr>
        <?php endforeach; ?>
    </table>

    <div style="margin-top:20px;">
        <a href="dashboard.php">← Back to Dashboard</a>
    </div>

</div>
</body>
</html>
