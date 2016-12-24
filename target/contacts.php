<?php
$variable = $_GET['xss'];
$a = $variable;
$b = $a;
echo $b;

$variable1 = htmlspecialchars($_GET['xss1']);
$a1 = $variable1;
$b1 = $a1;
echo $b1;

$variable = $_POST['xsspost'];
$a = $variable;
$b = $a;
echo $b;

$variable1 = htmlspecialchars($_POST['xsspost1']);
$a1 = $variable1;
$b1 = $a1;
echo $b1;

echo $_SESSION['login'];

$_COOKIES['login'] = $_POST['cookie'];

$g = $_REQUEST['lol'];
$var = $g; 
echo $var;


?>