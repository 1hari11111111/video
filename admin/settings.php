<?php
session_start();
require_once __DIR__ . "/../api/db.php";
if (!isset($_SESSION['admin_logged'])) { header("Location: login.php"); exit; }
$db = mongo_db();
$msg = "";
if ($_SERVER["REQUEST_METHOD"]==="POST"){
  $ref=intval($_POST["referral"]);
  $price=intval($_POST["price"]);
  $db->settings->updateOne(["key"=>"referral"],['$set'=>["value"=>$ref]],["upsert"=>true]);
  $db->settings->updateOne(["key"=>"default_price"],['$set'=>["value"=>$price]],["upsert"=>true]);
  $msg="Saved!";
}
$ref = $db->settings->findOne(["key"=>"referral"])["value"] ?? 100;
$price = $db->settings->findOne(["key"=>"default_price"])["value"] ?? 10;
?>
<form method=post>
Referral Reward: <input name=referral value="<?= $ref ?>"><br>
Default Price: <input name=price value="<?= $price ?>"><br>
<button>Save</button>
</form>
<?= $msg ?>
