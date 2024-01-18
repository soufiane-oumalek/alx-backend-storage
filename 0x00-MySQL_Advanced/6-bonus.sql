--script that creates a stored procedure AddBonus that adds a new correction for a student.
-- Drop the existing procedure if it exists
DROP PROCEDURE IF EXISTS AddBonus;

DELIMITER $$

CREATE PROCEDURE AddBonus(
    IN p_user_id INT,
    IN p_project_name VARCHAR(255),
    IN p_score INT)
BEGIN
    DECLARE project_id INT;
    INSERT INTO projects (name)
    SELECT p_project_name
    FROM DUAL
    WHERE NOT EXISTS (SELECT 1 FROM projects WHERE name = p_project_name);
    SELECT id INTO project_id FROM projects WHERE name = p_project_name LIMIT 1;
    INSERT INTO corrections (user_id, project_id, score) VALUES (p_user_id, project_id, p_score);
END $$
DELIMITER ;
