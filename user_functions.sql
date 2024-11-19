DELIMITER //
CREATE PROCEDURE GetUserCredentials(
    IN input_user_id INT,
    IN input_user_type Varchar(20)
)
BEGIN
    -- Retrieve User_Name and Password for the given user ID
    SELECT User_Name, Password
    FROM User
    WHERE User_ID = input_user_id AND User_Type=input_user_type;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetAllOperators()
BEGIN
    SELECT User_ID, User_Name, Email, Phone_Number, User_Type
    FROM User
    WHERE User_Type = 'Operator';
END //

DELIMITER //
CREATE PROCEDURE GetAllAdmins()
BEGIN
    SELECT User_ID, User_Name, Email, Phone_Number, User_Type
    FROM User
    WHERE User_Type = 'Admin';
END //
DELIMITER ;

DELIMITER //

CREATE TRIGGER before_insert_check_availability
BEFORE INSERT ON Parking_Lot
FOR EACH ROW
BEGIN
    DECLARE unavailable_count INT;

    -- Count the number of entries where Available = 'No'
    SELECT COUNT(*) INTO unavailable_count
    FROM Parking_Lot
    WHERE Available = 'No';

    -- Check if the count exceeds the limit
    IF unavailable_count >= 500 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot add more entries: Occupied lots exceed limit of 500';
    END IF;
END;
//

DELIMITER ;


DELIMITER //

CREATE TRIGGER CalculateParkingCharge
BEFORE INSERT ON Parking_Transaction
FOR EACH ROW
BEGIN
    DECLARE vehicle_type VARCHAR(50);
    DECLARE entry_time TIMESTAMP;
    DECLARE total_hours INT;
    DECLARE base_rate INT;
    DECLARE additional_rate INT;

    -- Fetch vehicle details from the Vehicle table
    SELECT Vehicle_Type, Entry_Time INTO vehicle_type, entry_time
    FROM Vehicle
    WHERE Vehicle_ID = NEW.Vehicle_ID;

    -- Calculate the total parked hours
   
    IF NEW.Exit_Time IS NOT NULL AND entry_time IS NOT NULL THEN
        SET total_hours = TIMESTAMPDIFF(HOUR, entry_time, NEW.Exit_Time);
    ELSE
        SET total_hours = 0; -- or handle the case as needed
    END IF;

        -- Calculate payment based on vehicle type and parked hours
        IF vehicle_type = '2-wheeler' THEN
            SET base_rate = 20;
            SET additional_rate = 10;
        ELSEIF vehicle_type = '4-wheeler' THEN
            SET base_rate = 30;
            SET additional_rate = 20;
        END IF;

        IF total_hours <= 3 THEN
            SET NEW.Payment_Amount = base_rate;
        ELSE
            SET NEW.Payment_Amount = base_rate + CEIL((total_hours - 3) / 3) * additional_rate;
        END IF;
END //

DELIMITER ;

DELIMITER //

CREATE FUNCTION update_user_details(
    in_user_id INT,
    in_user_name VARCHAR(50),
    in_email VARCHAR(50),
    in_phone_number VARCHAR(15),
    in_user_type VARCHAR(20),
    in_password VARCHAR(255)
) RETURNS VARCHAR(100)
DETERMINISTIC
BEGIN
    -- Check if the user exists
    IF EXISTS (SELECT 1 FROM User WHERE User_ID = in_user_id) THEN
        -- Update user details
        IF in_user_name IS NOT NULL THEN
            UPDATE User SET User_Name = in_user_name WHERE User_ID = in_user_id;
        END IF;

        IF in_email IS NOT NULL THEN
            UPDATE User SET Email = in_email WHERE User_ID = in_user_id;
        END IF;

        IF in_phone_number IS NOT NULL THEN
            UPDATE User SET Phone_Number = in_phone_number WHERE User_ID = in_user_id;
        END IF;

        IF in_user_type IS NOT NULL THEN
            UPDATE User SET User_Type = in_user_type WHERE User_ID = in_user_id;
        END IF;

        IF in_password IS NOT NULL THEN
            UPDATE User SET Password = in_password WHERE User_ID = in_user_id;
        END IF;

        RETURN 'User details updated successfully.';
    ELSE
        RETURN 'User ID not found.';
    END IF;
END//

DELIMITER ;


DELIMITER $$

CREATE TRIGGER UpdateParkingAvailability
AFTER INSERT ON Vehicle
FOR EACH ROW
BEGIN
    -- Declare a variable to hold the Parking_Lot_ID
    DECLARE available_spot INT;

    -- Find the minimum Parking_Lot_ID where Available = 'Yes'
    SELECT MIN(Parking_Lot_ID)
    INTO available_spot
    FROM Parking_Lot
    WHERE Available != 'No';

    -- Update the availability of the selected parking lot
    IF available_spot IS NOT NULL THEN
        UPDATE Parking_Lot
        SET Available = 'No'
        WHERE Parking_Lot_ID = available_spot;
    END IF;
END$$

DELIMITER ;


DELIMITER $$

CREATE TRIGGER ReleaseParkingSpot
AFTER INSERT ON Parking_Transaction
FOR EACH ROW
BEGIN
    -- Declare a variable to hold the Parking_Lot_ID
    DECLARE unavailable_spot INT;

    -- Find the first unavailable parking spot
    SELECT MIN(Parking_Lot_ID)
    INTO unavailable_spot
    FROM Parking_Lot
    WHERE Available = 'No';

    -- Update the availability of the selected parking lot
    IF unavailable_spot IS NOT NULL THEN
        UPDATE Parking_Lot
        SET Available = 'Yes'
        WHERE Parking_Lot_ID = unavailable_spot;
    END IF;
END$$

DELIMITER ;