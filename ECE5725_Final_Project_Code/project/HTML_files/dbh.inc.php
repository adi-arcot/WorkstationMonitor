<?php
    $dsn = "mysql:host=localhost;dbname=final_project";
    $dbusername = "default";
    $dbpassword = "password";



    try{
        $pdo = new PDO($dsn, $dbusername, $dbpassword);
        $pdo -> setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    catch (PDOException $e) {
        echo "Connection Failed: " . $e->geMessage();
    }