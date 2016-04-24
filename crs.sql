DROP DATABASE IF EXISTS crs;
CREATE DATABASE crs1;
\c crs1

CREATE TABLE administrator (
    email varchar(35),
    password varchar(35),
    background text,
    PRIMARY KEY (email));

INSERT INTO administrator VALUES ('test@test.com', 'password');

CREATE TABLE class (
    class_code int,
    class_name varchar(35),
    background text references administrator(background),
    PRIMARY KEY (class_code));

INSERT INTO class VALUES (1234, 'History');
INSERT INTO class VALUES (1111, 'Geography');

CREATE TABLE question (
    question_id serial,
    question_type int not null,
    question text,
    admin_comments text,
    image_filepath text,
    PRIMARY KEY (question_id));
    
INSERT INTO question VALUES (DEFAULT, 0, 'What is 2 + 2?', 'This question is a math question.', 'file path goes here');
INSERT INTO question VALUES (DEFAULT, 1, 'What color is the sky?', 'A sky question.', 'file path goes here');
INSERT INTO question VALUES (DEFAULT, 2, 'Where is Peru?', 'Map Question', null);

CREATE TABLE multiple_choice_question (
    question_id int references question(question_id),
    option_a text,
    option_b text,
    option_c text,
    option_d text,
    option_e text,
    correct_answer varchar(1));
    
INSERT INTO multiple_choice_question VALUES (1, '3', '7', '4', null, null, 3);

CREATE TABLE map_question (
    question_id int references question(question_id),
    map_filepath text,
    answer_coordinates text);
    
INSERT INTO map_question VALUES (3, 'filepath', '235, 76');

CREATE TABLE answers (
    date date,
    status varchar(35),
    class_code int references class(class_code),
    question_id int references question(question_id),
    answer_filepath text,
    share boolean;)
    
INSERT INTO answers VALUES('2016-1-18', 'undisplay', 1234, 1, 'bloop',FALSE);
INSERT INTO answers VALUES(null, 'undisplay', 1234, 1, null,FALSE);
INSERT INTO answers VALUES(null, 'undisplay', 1111, 2, null,FALSE);