<?php
// ================================================================
//  SAVE TOKEN API (Called by Bot-A)
//  Saves:
//   • token
//   • user_id
//   • video info
//   • expiry (minutes)
// ================================================================

header("Content-Type: application/json");

require_once __DIR__ . "/db.php";   // MongoDB connection

// -------------- GET POST DATA -----------------
$input = json_decode(file_get_contents("php://input"), true);

if (!$input) {
    echo json_encode(["status" => "error", "message" => "Invalid JSON input"]);
    exit;
}

$token      = $input["token"]      ?? null;
$user_id    = $input["user_id"]    ?? null;
$video_data = $input["video"]      ?? null;
$minutes    = $input["expires"]    ?? 5;

// -------------- VALIDATION -----------------
if (!$token || !$user_id || !$video_data) {
    echo json_encode(["status" => "error", "message" => "Missing fields"]);
    exit;
}

try {

    $expiry = new MongoDB\BSON\UTCDateTime((time() + ($minutes * 60)) * 1000);

    $db->tokens->insertOne([
        "token"    => $token,
        "user_id"  => intval($user_id),
        "video"    => $video_data,
        "expires"  => $expiry,
        "used"     => false,
        "created"  => new MongoDB\BSON\UTCDateTime()
    ]);

    echo json_encode(["status" => "success", "message" => "Token saved"]);

} catch (Exception $e) {

    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>
