<?php
session_start();
require_once __DIR__ . "/../api/db.php";
if (!isset($_SESSION['admin_logged'])) { header("Location: login.php"); exit; }
$db=mongo_db();
$users=$db->users->find();
?>
<table border=1>
<tr><th>ID</th><th>Points</th><th>Banned</th></tr>
<?php foreach($users as $u): ?>
<tr>
<td><?= $u['user_id'] ?></td>
<td><?= $u['points'] ?></td>
<td><?= $u['banned']?'Yes':'No' ?></td>
</tr>
<?php endforeach; ?>
</table>
