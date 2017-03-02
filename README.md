impleAuth:**
===========

SimpleAuth is a simple, secure, and fast service for setting creating and deleting users, and managing their sessions, all behind a simple json api. SimpleAuth is really simple.

**What can you do with SimpleAuth?**

- Log users in
- Log users out
- Set session variables
- Unset session variables
- Read session variables

**What about creating those users?** 

With SimpleAuth, you can also:

- Register Users
- Unregister Users

**What about user roles?**

With SimpleAuth, you can also:

- Create user roles
- Associate users to roles
- Remove user roles
- Disassociate users from user roles

**It's just that simple.**

SimpleAuth is so simple, you can read the all documentation right here, right now!

**Quick Start:**
=====================

Log Users In:
-------------

**Request:**

    {
    	command: "log_in",
    	user_name: "simpleauth@email.com",
    	password: "some password"
    }
    
**Possible responses:**

   Success:
   
    {
    	success: "true",
    	cookie: "abc123"
    }

Failure:

    {
    	success: "false",
    	error: "User already logged in.",
    	error_code: "LUI_1"
    }

Log Users Out:
--------------

**Possible requests:**
 
    {
    	command: "log_out",
    	cookie: "abc123"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true",
    }

Failure:

    {
    	success: "false",
    	error: "User is already logged out."
    	error_code: "LOU_1"
    }
    
Set Session Variables:
--------------

**Possible requests:**

Set single variable:

    {
        command: "set_session_var",
        cookie: "abc123",
    	session_key: "some_variable_key",
    	session_value: "{wow: such_value}"
    }
Set multiple variables:

    {
        command: "set_session_var",
        cookie: "abc123",
    	session_keys: [
	    	"first_key",
	    	"second_key"
        ],
    	session_values: [
	    	"first_value",
	    	"second_value: {'wow': 'such_value'}"
    	]
    }
    
**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
    	error: "Unknown cookie."
    	error_code: "SSV_1"
    }

Unset Session Variables:
--------------

**Possible requests:**

Unset a single variable:

    {
        command: "unset_session_var",
        cookie: "abc123",
        session_key: "some_key"
    }

Unset a multiple variables:

    {
        command: "unset_session_var",
        cookie: "abc123",
        session_keys: [
            "first_key",
            "second_key"
        ]
    }

**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
    	error: "Unknown cookie."
    	error_code: "USV_1"
    }

Read Session Variables:
--------------

**Possible requests:**

Read a single variable:

    {
        command: "read_session_var",
        cookie: "abc123",
        session_key: "some_session_key"
    }

Read a multiple variables:

    {
        command: "read_session_var",
        cookie: "abc123",
        session_keys: [
	        "first",
	        "second_key"
	    ]
    }
**Possible responses:**

   Success:
   
    {
    	success: "true",
    	session_variables: {
	    	"some_key": "some_value",
	    	"another_key": "another_value"
    	}
    }

Failure:

    {
    	success: "false",
    	error: "Unknown cookie."
    	error_code: "RSV_1"
    }
    
Register a User:
--------------

**Possible requests:**

    {
        command: "register_user",
        user_name: "newuser@gmail.com",
        password: "some password"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
        error: "User already exists",
        error_code "RU_1"
    }
       
Unregister a User:
--------------

**Possible requests:**

Using cookie if user is logged in.

    {
        command: "unregister_user",
        user_name: "newuser@gmail.com",
        cookie: "abc123"
    }

Using an admin key:

    {
        command: "unregister_user",
        user_name: "newuser@gmail.com",
        admin_key: "super_secret_key"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
        error: "User does not exists",
        error_code "UU_1"
    }
     
Register a User Role:
--------------

**Possible requests:**

    {
        command: "register_user_role",
        admin_key: "super_secret_key",
        user_role: "some_user_role"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
        error: "User role already exists",
        error_code "RUR_1"
    }

Associate a User to a Role:
--------------

**Possible requests:**

    {
        command: "associate_user_role",
        admin_key: "super_secret_key",
        user_name: "simpleauth@email.com",
        user_role: "some_user_role"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
        error: "User does not exist",
        error_code "AUR_1"
    }

    
Unregister a User Role:
--------------

**Possible requests:**

    {
        command: "unregister_user_role",
        admin_key: "super_secret_key",
        user_role: "some_user_role"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
        error: "User role does not exists",
        error_code "UUR_1"
    }

Disassociate a User to a Role:
--------------

**Possible requests:**

    {
        command: "disassociate_user_role",
        admin_key: "super_secret_key",
        user_name: "simpleauth@email.com",
        user_role: "some_user_role"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
        error: "User does not exist",
        error_code "DUR_1"
    }


**All Error Codes:**
================

All error codes are prepended by their command, then followed by a number.

