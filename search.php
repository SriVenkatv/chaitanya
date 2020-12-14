<?php

include_once('database.php');

if (empty($_GET)) {
    echo "FALSE";
}
else {
    $addr = htmlspecialchars($_GET["mac"]);
    $addr = "%". $addr . "%";

    $sql = "SELECT * FROM reports WHERE MACS LIKE '{$addr}' ORDER BY MACS";
    $find = $db->query($sql);

    $arr = array(); 
    while($row = $find->fetchArray(SQLITE3_ASSOC) ){
         $arr[] = $row['Device']. " | " . $row['VLANS'] . " | " . $row['port'] . " | " . $row['MACS'];
    }

    $totnum = count($arr);
    if ($totnum == 0){
        $count = $db->query('SELECT count(*) FROM switches');
        while($row1 = $count->fetchArray(SQLITE3_ASSOC)) {
            $noDevices = $row1['count(*)'];
            echo "Not Found in $noDevices devices" . "<br>";
        }
    }

    $res = array_unique($arr);
    $len = count($res);
    for($i = 0; $i < $len; $i++){
        echo $res[$i]. "<br>";
    }
}
$db->close();

//http://localhost/track/search.php?mac=11-22
?>