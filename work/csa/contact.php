<?php
/* ============================================================
   CSA contact form handler — works on standard cPanel/PHP hosting.
   CONFIGURE: set $TO to the CSA team member's email address before go-live.
   ============================================================ */

$TO        = 'info@csatab.com';           // <-- recipient on the CSA team
$FROM_ADDR = 'website@csatab.com';             // sending identity (must be a domain mailbox on most hosts)
$SUBJECT   = 'New Quote Request — csatab.com';

/* uploaded plans: saved to disk (never emailed as attachments — sets can run
   hundreds of MB, past what any mailbox accepts) and linked from the email. */
$UPLOAD_DIR       = __DIR__ . '/uploads';
$UPLOAD_URL_BASE  = 'https://csatab.com/uploads';
$MAX_TOTAL_BYTES  = 125 * 1024 * 1024; // keep under the server's 128MB post_max_size
$ALLOWED_EXT      = ['pdf','dwg','dxf','dwf','zip','rar','7z','jpg','jpeg','png','tif','tiff','doc','docx','xls','xlsx'];

/* every submission is logged here too — outside the web root — so a lead is
   never lost even if an email fails to send or land. */
$SUBMISSIONS_LOG  = dirname(dirname(__DIR__)) . '/contact-submissions.log';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  http_response_code(405);
  echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
  exit;
}

/* if the whole request exceeded post_max_size, PHP empties $_POST and
   $_FILES before your code ever runs — catch that case with a clear message
   instead of the generic "complete all fields" error below. */
if (empty($_POST) && empty($_FILES) && (int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 0) {
  http_response_code(413);
  echo json_encode(['ok' => false, 'error' => 'Your files were too large for one submission (120MB limit). Please remove a file and try again, or email them directly to info@csatab.com.']);
  exit;
}

/* honeypot — bots fill every field */
if (!empty($_POST['website'])) {
  echo json_encode(['ok' => true]); // pretend success, drop silently
  exit;
}

$clean = function ($key, $max = 500) {
  $v = isset($_POST[$key]) ? trim($_POST[$key]) : '';
  $v = str_replace(["\r", "\n"], ' ', $v);      // header-injection guard
  return mb_substr($v, 0, $max);
};

$name    = $clean('name', 120);
$company = $clean('company', 160);
$email   = $clean('email', 160);
$phone   = $clean('phone', 40);
$service = $clean('service', 80);
$message = isset($_POST['message']) ? mb_substr(trim($_POST['message']), 0, 4000) : '';

if ($name === '' || $email === '' || $phone === '' || $service === '' || $message === '') {
  http_response_code(422);
  echo json_encode(['ok' => false, 'error' => 'Please complete all required fields.']);
  exit;
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
  http_response_code(422);
  echo json_encode(['ok' => false, 'error' => 'Please enter a valid email address.']);
  exit;
}

/* ---- handle uploaded plans (optional) ---- */
$planLinks   = [];   // ["Original Name.pdf (12.3 MB)" => full URL]
$planErrors  = [];

if (!empty($_FILES['plans']) && is_array($_FILES['plans']['name'])) {
  $count = count($_FILES['plans']['name']);
  $totalBytes = 0;

  for ($i = 0; $i < $count; $i++) {
    $err = $_FILES['plans']['error'][$i];
    if ($err === UPLOAD_ERR_NO_FILE) continue;

    $origName = $_FILES['plans']['name'][$i];
    if ($err !== UPLOAD_ERR_OK) {
      $planErrors[] = "{$origName}: upload error ({$err})";
      continue;
    }

    $size = (int) $_FILES['plans']['size'][$i];
    $totalBytes += $size;
    if ($totalBytes > $MAX_TOTAL_BYTES) {
      $planErrors[] = "{$origName}: skipped — combined upload exceeded the 120MB limit";
      continue;
    }

    $ext = strtolower(pathinfo($origName, PATHINFO_EXTENSION));
    if (!in_array($ext, $ALLOWED_EXT, true)) {
      $planErrors[] = "{$origName}: file type not accepted";
      continue;
    }

    if (!is_dir($UPLOAD_DIR)) {
      @mkdir($UPLOAD_DIR, 0750, true);
      @file_put_contents($UPLOAD_DIR . '/.htaccess', "Options -Indexes\nphp_flag engine off\nRemoveHandler .php .phtml .php3 .php4 .php5 .php7 .php8 .pl .py .cgi .asp .aspx\nAddType text/plain .php .phtml .php3 .php4 .php5 .php7 .php8 .pl .py .cgi .asp .aspx\n");
    }

    $safeName = bin2hex(random_bytes(16)) . '.' . $ext;
    $dest = $UPLOAD_DIR . '/' . $safeName;

    if (move_uploaded_file($_FILES['plans']['tmp_name'][$i], $dest)) {
      @chmod($dest, 0640);
      $label = $origName . ' (' . round($size / 1024 / 1024, 1) . ' MB)';
      $planLinks[$label] = $UPLOAD_URL_BASE . '/' . $safeName;
    } else {
      $planErrors[] = "{$origName}: could not be saved";
    }
  }
}

$body  = "New quote request from csatab.com\n";
$body .= "=================================\n\n";
$body .= "Name:     {$name}\n";
if ($company !== '') $body .= "Company:  {$company}\n";
$body .= "Email:    {$email}\n";
$body .= "Phone:    {$phone}\n";
$body .= "Service:  {$service}\n\n";
$body .= "Message:\n{$message}\n\n";

if ($planLinks) {
  $body .= "Attached Plans:\n";
  foreach ($planLinks as $label => $url) {
    $body .= "- {$label}\n  {$url}\n";
  }
  $body .= "\n";
}
if ($planErrors) {
  $body .= "Upload issues (not sent):\n";
  foreach ($planErrors as $e) $body .= "- {$e}\n";
  $body .= "\n";
}

$body .= "---\nSent " . date('Y-m-d H:i:s T') . " from " . ($_SERVER['REMOTE_ADDR'] ?? 'unknown IP') . "\n";

/* durable record — written regardless of mail() outcome */
@file_put_contents(
  $SUBMISSIONS_LOG,
  json_encode([
    'time'    => date('c'),
    'name'    => $name,
    'company' => $company,
    'email'   => $email,
    'phone'   => $phone,
    'service' => $service,
    'message' => $message,
    'plans'   => $planLinks,
    'ip'      => $_SERVER['REMOTE_ADDR'] ?? null,
  ]) . "\n",
  FILE_APPEND | LOCK_EX
);

$headers  = "From: CSA Website <{$FROM_ADDR}>\r\n";
$headers .= "Reply-To: {$name} <{$email}>\r\n";
$headers .= "X-Mailer: PHP/" . phpversion() . "\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

/* the -f flag sets the envelope sender to an @csatab.com address so it lines
   up with the domain's SPF record and the visible From header — mismatched
   envelope/header senders are a common cause of mail silently landing in
   spam or getting dropped. */
$sent = @mail($TO, $SUBJECT, $body, $headers, '-f' . $FROM_ADDR);

if ($sent) {
  echo json_encode(['ok' => true]);
} else {
  http_response_code(500);
  echo json_encode(['ok' => false, 'error' => 'Mail could not be sent.']);
}
