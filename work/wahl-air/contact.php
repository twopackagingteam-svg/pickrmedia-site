<?php
// Wahl Air — contact form endpoint (PHP mail(), standard cPanel hosting)
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['ok'=>false,'error'=>'method']); exit; }
if (!empty($_POST['company'])) { echo json_encode(['ok'=>true]); exit; } // honeypot

$TO = 'info@wahlair.com'; // TODO: confirm with Chris this is where website leads should go
$first = trim(strip_tags($_POST['first'] ?? ''));
$last  = trim(strip_tags($_POST['last'] ?? ''));
$email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);
$phone = trim(strip_tags($_POST['phone'] ?? ''));
$svc   = trim(strip_tags($_POST['service'] ?? ''));
$msg   = trim(strip_tags($_POST['message'] ?? ''));
if (!$first || !$email || !$phone) { http_response_code(422); echo json_encode(['ok'=>false,'error'=>'missing fields']); exit; }

$body = "New website service request\n\n"
      . "Name:    $first $last\n"
      . "Phone:   $phone\n"
      . "Email:   $email\n"
      . "Service: $svc\n\n"
      . "Message:\n$msg\n\n"
      . "— wahlair.com contact form · " . date('Y-m-d H:i T');
$headers = "From: Wahl Air Website <noreply@wahlair.com>\r\nReply-To: $email\r\n";
$ok = @mail($TO, "Service request — $first $last ($svc)", $body, $headers);
echo json_encode(['ok' => (bool)$ok, 'error' => $ok ? null : 'mail failed']);
