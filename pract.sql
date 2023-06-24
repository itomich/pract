create role Admin with password 'admin12345';
alter role Admin LOGIN;
Grant connect on database "pract" to Admin;

create table Data(
	ID_Data Serial not null constraint PK_Inventory_brand primary key,
	Data_Address_ID varchar(20) not null,
	Data_Date_Time timestamp not null,
	Data_Request_Method varchar(50) not null,
	Data_Status_Code varchar(10) not null,
	Data_Response_Size varchar(10) not null,
	Data_Referer varchar(20) not null,
	Data_User_Agent varchar not null
);

