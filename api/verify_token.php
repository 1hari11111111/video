<?php
// ================================================================
//  VERIFY TOKEN API (Called by Bot-B)
//  Verifies:
//    • token exists
//    • token is not expired
//    • token is unused
//  Returns:
//    • video data (file_id, channel, title, etc.)
// ================================================================

header("Content-Type: application/json");

require_once __DIR__ . "/db.php";   // MongoDB connection

if (!isset($_GET["token"])) {
    echo json_encode(["status" => "error", "message" => "Token missing"]);
    exit;
}

$token = $_GET["token"];

try {
    $data = $db->tokens->findOne(["token" => $token]);

    if (!$data) {
        echo json_encode(["status" => "error", "message" => "Invalid token"]);
        exit;
    }

    // Check if already used
    if (isset($data["used"]) && $data["used"] === true) {
        echo json_encode(["status" => "error", "message" => "Token already used"]);
        exit;
    }

    // Check expiry
    $now = new MongoDB\BSON\UTCDateTime();
    if ($data["expires"] < $now) {
        echo json_encode(["status" => "error", "message" => "Token expired"]);
        exit;
    }

    // Mark token as used
    $db->tokens->updateOne(
        ["token" => $token],
        ['$set' => ["used" => true]]
    );

    // Return video info
    echo json_encode([
        "status" => "success",
        "video"  => $data["video"]
    ]);

} catch (Exception $e) {

    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>
