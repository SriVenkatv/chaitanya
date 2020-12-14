<?php

include_once('config.php');

$ip = $_GET['ip'];
$port = $_GET['port'];
$community = $_GET['community'];
$version = $_GET['version'];

if (empty($ip) || empty($port) || empty($community) || empty($version)) {
    echo "FALSE";
}
else {
    $switches = $db->query('SELECT * FROM switches');
    $count = 0;
    while ($row = $switches->fetchArray()) {
        if($row['ip']==$ip && $row['port']==$port && $row['community']==$community && $row['version']==$version){
            $count = $count + 1;
            break;
        }
    }

    if ($count ==0){
        $db->exec("INSERT INTO switches (ip, port, community, version) VALUES ('$ip', '$port', '$community', '$version')");
        echo "OK";
    }
    else {
        echo "FALSE";
    }
}

$db->close();
//localhost/track/addDevice.php?ip=192.168.1.22&port=1166&community=public&version=2

?>