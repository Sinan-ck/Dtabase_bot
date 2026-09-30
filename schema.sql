CREATE DATABASE IF NOT EXISTS atliq_tshirts;
USE atliq_tshirts;

CREATE TABLE t_shirts (
  t_shirt_id INT NOT NULL AUTO_INCREMENT,
  brand ENUM('Van Huesen','Levi','Nike','Adidas') NOT NULL,
  color ENUM('Red','Blue','Black','White') NOT NULL,
  size ENUM('XS','S','M','L','XL') NOT NULL,
  price INT,
  stock_quantity INT NOT NULL,
  PRIMARY KEY (t_shirt_id),
  CONSTRAINT t_shirts_chk_1 CHECK (price BETWEEN 10 AND 50)
);

CREATE TABLE discounts (
  discount_id INT NOT NULL AUTO_INCREMENT,
  t_shirt_id INT NOT NULL,
  pct_discount DECIMAL(5,2),
  PRIMARY KEY (discount_id),
  CONSTRAINT discounts_ibfk_1 FOREIGN KEY (t_shirt_id) REFERENCES t_shirts (t_shirt_id),
  CONSTRAINT discounts_chk_1 CHECK (pct_discount BETWEEN 0 AND 100)
);

INSERT INTO t_shirts (brand, color, size, price, stock_quantity) VALUES
  ('Van Huesen','Red','S',15,70),
  ('Adidas','Black','XS',17,46),
  ('Levi','White','XS',44,94);

INSERT INTO discounts (t_shirt_id, pct_discount) VALUES
  (1,10.00),
  (2,15.00),
  (3,20.00);
