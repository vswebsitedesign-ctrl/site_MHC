<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    
    $to_email = "info@mikes-house-clearance.co.uk"; 
    $subject = "New Quote Request - Mike's House Clearance";
    $first_name = filter_input(INPUT_POST, 'first-name', FILTER_SANITIZE_SPECIAL_CHARS);
    $surname    = filter_input(INPUT_POST, 'surname', FILTER_SANITIZE_SPECIAL_CHARS);
    $phone      = filter_input(INPUT_POST, 'telephone', FILTER_SANITIZE_SPECIAL_CHARS);
    $email      = filter_input(INPUT_POST, 'email', FILTER_VALIDATE_EMAIL);
    $postcode   = filter_input(INPUT_POST, 'postcode', FILTER_SANITIZE_SPECIAL_CHARS);
    $message    = filter_input(INPUT_POST, 'message', FILTER_SANITIZE_SPECIAL_CHARS);
    $clearance_types = [];
    if (isset($_POST['clearance-type']) && is_array($_POST['clearance-type'])) {
        foreach ($_POST['clearance-type'] as $type) {
            $clearance_types[] = htmlspecialchars($type);
        }
    }
    $clearance_string = !empty($clearance_types) ? implode(", ", $clearance_types) : "";
    if (empty($first_name) || empty($phone) || empty($postcode) || empty($clearance_string)) {
        echo "Error: Please fill in all mandatory fields (*).";
        exit;
    }
    $email_body = "You have received a new quote request from your website form.\n\n";
    $email_body .= "--- CUSTOMER DETAILS ---\n";
    $email_body .= "Name: " . $first_name . (!empty($surname) ? " " . $surname : "") . "\n";
    $email_body .= "Phone Number: " . $phone . "\n";
    $email_body .= "Email Address: " . ($email ? $email : "Not provided") . "\n";
    $email_body .= "Postcode: " . $postcode . "\n\n";
    $email_body .= "--- REQUEST DETAILS ---\n";
    $email_body .= "Type of Clearance: " . $clearance_string . "\n\n";
    $email_body .= "--- ADDITIONAL DETAILS ---\n";
    $email_body .= (!empty($message)) ? $message : "No additional details provided.";
    $from_email = "no-reply@mikes-house-clearance.co.uk"; 
    $headers = "From: Mike's House Clearance <" . $from_email . ">\r\n";
    if ($email) {
        $headers .= "Reply-To: " . $email . "\r\n";
    }
    $headers .= "X-Mailer: PHP/" . phpversion();
    if (mail($to_email, $subject, $email_body, $headers)) {
        header("Location: thank-you.html"); 
        exit;
    } else {
        echo "Error: Server failed to send email.";
    }
} else {
    header("HTTP/1.1 403 Forbidden");
    echo "Direct access forbidden.";
}
?>
