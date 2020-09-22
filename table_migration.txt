CREATE TABLE `address` (
  `idaddress` int(11) NOT NULL AUTO_INCREMENT,
  `iduser` int(11) NOT NULL,
  `address_line` varchar(45) NOT NULL,
  `unit_no` varchar(45) NOT NULL,
  `zipcode` varchar(45) NOT NULL,
  PRIMARY KEY (`idaddress`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `bill_items` (
  `idtransaction` int(11) NOT NULL,
  `idproduct` int(11) NOT NULL,
  `product_qty` int(11) NOT NULL DEFAULT '1',
  KEY `fk_billitem_idtransaction_idx` (`idtransaction`),
  KEY `fk_billitem_idprocut_idx` (`idproduct`),
  CONSTRAINT `fk_billitem_idprocut` FOREIGN KEY (`idproduct`) REFERENCES `product_listing` (`idproduct_listing`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_billitem_idtransaction` FOREIGN KEY (`idtransaction`) REFERENCES `transaction` (`idtransaction`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cart` (
  `iduser` int(11) NOT NULL,
  `idproduct` int(11) NOT NULL,
  `qty` int(11) DEFAULT NULL,
  PRIMARY KEY (`iduser`,`idproduct`),
  KEY `fk_cart_idproduct_idx` (`idproduct`),
  CONSTRAINT `fk_cart_idproduct` FOREIGN KEY (`idproduct`) REFERENCES `product_listing` (`idproduct_listing`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cart_iduser` FOREIGN KEY (`iduser`) REFERENCES `user` (`iduser`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `login_origin_history` (
  `iduser` int(11) NOT NULL,
  `ip_address` int(11) NOT NULL,
  PRIMARY KEY (`iduser`,`ip_address`),
  CONSTRAINT `fk_login_origin_history_iduser` FOREIGN KEY (`iduser`) REFERENCES `user` (`iduser`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `product_images` (
  `idproduct` int(11) NOT NULL,
  `imageurl` varchar(255) NOT NULL,
  PRIMARY KEY (`idproduct`,`imageurl`),
  CONSTRAINT `fk_image_productid` FOREIGN KEY (`idproduct`) REFERENCES `product_listing` (`idproduct_listing`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `product_listing` (
  `idproduct_listing` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `price` double NOT NULL,
  `iduser` int(11) NOT NULL,
  `removed` tinyint(4) NOT NULL DEFAULT '0',
  `stock_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`idproduct_listing`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;

CREATE TABLE `pw_history` (
  `fk_iduser` int(11) NOT NULL,
  `password` varchar(45) NOT NULL,
  `date_changed` datetime(6) NOT NULL,
  PRIMARY KEY (`fk_iduser`,`password`),
  KEY `iduser_idx` (`fk_iduser`),
  CONSTRAINT `pw_history_to_user` FOREIGN KEY (`fk_iduser`) REFERENCES `user` (`iduser`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `transaction` (
  `idtransaction` int(11) NOT NULL AUTO_INCREMENT,
  `idaddress` int(11) NOT NULL,
  `iduser_buyer` int(11) NOT NULL,
  `iduser_seller` int(11) NOT NULL,
  `total_price` double NOT NULL DEFAULT '0',
  PRIMARY KEY (`idtransaction`),
  KEY `fk_transaction_idseller_idx` (`iduser_seller`),
  KEY `fk_transaction_idaddress_idx` (`idaddress`),
  CONSTRAINT `fk_transaction_idaddress` FOREIGN KEY (`idaddress`) REFERENCES `address` (`idaddress`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_transaction_idseller` FOREIGN KEY (`iduser_seller`) REFERENCES `user` (`iduser`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `user` (
  `iduser` int(11) NOT NULL AUTO_INCREMENT,
  `fname` varchar(45) NOT NULL,
  `lname` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `password` varchar(60) NOT NULL,
  `total_revenue` double NOT NULL DEFAULT '0',
  `rating_avg` double NOT NULL DEFAULT '0',
  `password_change_date` timestamp(6) NULL DEFAULT NULL,
  `incorrect_login_count` int(11) NOT NULL DEFAULT '0',
  `user_join_date` datetime(6) NOT NULL,
  `removed` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`iduser`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
