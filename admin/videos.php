<?php
session_start();
require_once __DIR__ . "/../api/db.php";

if (!isset($_SESSION["admin_logged"]) || $_SESSION["admin_logged"] !== true) {
    header("Location: login.php");
    exit;
}

$db = mongo_db();
$videos = $db->videos->find([], ["sort" => ["_id" => -1]]);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Manage Videos</title>
    <style>
        body {
            background: #121212;
            font-family: Arial;
            color: #fff;
            margin: 0;
            padding: 0;
        }
        .header {
            background: #1f1f1f;
            padding: 20px;
            font-size: 24px;
            text-align: center;
            font-weight: bold;
        }
        .container {
            padding: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 25px;
        }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #333;
            font-size: 15px;
        }
        th {
            background: #222;
        }
        a.btn {
            padding: 8px 14px;
            background: #0084ff;
            color: white;
            border-radius: 6px;
            text-decoration: none;
            font-size: 14px;
        }
        a.delete-btn {
            background: #ff3b3b;
        }
        .top-menu a {
            margin-right: 10px;
            color: #00aaff;
            text-decoration: none;
        }
    </style>
</head>
<body>

<div class="header">Manage Videos</div>

<div class="container">

    <div class="top-menu">
        <a href="dashboard.php">⬅ Back</a>
        <a href="add_video.php">➕ Add New Video</a>
    </div>

    <table>
        <tr>
            <th>Title</th>
            <th>Category</th>
            <th>Channel</th>
            <th>Price</th>
            <th>Action</th>
        </tr>

        <?php foreach ($videos as $v): ?>
        <tr>
            <td><?= $v["title"] ?></td>
            <td><?= $v["category"] ?></td>
            <td><?= $v["channel"] ?></td>
            <td><?= $v["price"] ?></td>
            <td>
                <a class="btn delete-btn" 
                   href="videos.php?delete=<?= $v['_id'] ?>"
                   onclick="return confirm('Delete this video?')">Delete</a>
            </td>
        </tr>
        <?php endforeach; ?>
    </table>

</div>

</body>
</html>

<?php
// ------------------ DELETE FUNCTION ------------------
if (isset($_GET["delete"])) {
    $id = $_GET["delete"];

    try {
        $db->videos->deleteOne(["_id" => new MongoDB\BSON\ObjectId($id)]);
        echo "<script>window.location='videos.php';</script>";
    } catch (Exception $e) {
        echo "<script>alert('Error deleting video');</script>";
    }
}
?>
