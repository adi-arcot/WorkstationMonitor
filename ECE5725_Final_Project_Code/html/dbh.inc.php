<?php
    $dsn = "mysql:host=localhost;dbname=final_project";
    $dbusername = "default";
    $dbpassword = "password";
    $databasename = "final_project";



    try{
        $pdo = new PDO($dsn, $dbusername, $dbpassword, $databasename );
        $pdo -> setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    catch (PDOException $e) {
        echo "Connection Failed: " . $e->geMessage();
    }