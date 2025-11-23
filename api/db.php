<?php
// ================================================================
//  MongoDB Connection (PHP)
//  Used by: save_token.php, verify_token.php, admin panel
// ================================================================

// ----------------------------
// CHANGE THIS IF USING ATLAS
// ----------------------------
$MONGO_URI = "mongodb://localhost:27017";   // local MongoDB
$DB_NAME = "telegram_video_system";

// If using MongoDB Atlas, example:
// $MONGO_URI = "mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority";

try {
    require_once __DIR__ . '/vendor/autoload.php';  // MongoDB PHP SDK

    $client = new MongoDB\Client($MONGO_URI);
    $db = $client->$DB_NAME;

} catch (Exception $e) {
    http_response_code(500);
    die(json_encode([
        "status" => "error",
        "message" => $e->getMessage()
    ]));
}
?>
