**SimpleAuth:**
===========

SimpleAuth is a simple, secure, and fast micro-service for setting creating and deleting users, and managing their sessions, all behind a simple json api. SimpleAuth is really simple.

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
        "command": "log_in",
        "user_name": "example_user@gmail.com",
        "password": "example_password"
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
    	"command": "log_out",
    	"cookie": "abc123"
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

    {
        "command": "set_session_vars",
        "cookie": "abc123",
    	"session_vars": {
	    	"first_key": "first_value",
	    	"second_key": "second_value"
    	}
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

    {
        "command": "unset_session_vars",
        "cookie": "abc123",
        "session_keys": [
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

    {
        "command": "read_session_vars",
        "cookie": "abc123",
        "session_keys": [
	        "first_key",
	        "second_key"
	    ]
    }
**Possible responses:**

   Success:
   
    {
    	success: "true",
    	session_vars: {
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
        "command": "register_user",
        "user_name": "example_user@gmail.com",
        "password": "example_password"
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
        "command": "unregister_user",
        "user_name": "newuser@gmail.com",
        "cookie": "abc123"
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
        "command": "register_role",
        "admin_key": "super_secret_key",
        "role_name": "example_role"
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
        "command": "associate_user_role",
        "admin_key": "super_secret_key",
        "user_name": "example_user@gmail.com",
        "role_name": "example_role"
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
        "command": "unregister_role",
        "admin_key": "super_secret_key",
        "role_name": "example_role"
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
        "command": "disassociate_user_role",
        "admin_key": "super_secret_key",
        "user_name": "example_user@gmail.com",
        "role_name": "example_role"
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

**Handling Google Identity Toolkit:**
================

Google Idenity Toolkie (gitkit) users have no password, yet need to have an account on file with the email address if their token is verified with their third party source (such as Google or Facebook).

For initial registration, an account will have an email address in which the authentication system will either:

1) Register the user.
2) Log the user in (mark their session as active).
3) Register the user and log the user in.
	
These three possible scenarios, when given an email address which should only happen if the service (typically a web server) knows the cookie associated with the email address is verified with the third party (typically Google or Facebook) will happen all at once and should only happen when a web server sees that a request has a valid `google_identity_token` cookie, but no native application authentication cookie. Because of this, it's named `handle_only_gitkit_token` as it should occur only when third party cookie is present and no native cookie exists.

Handle Only Gitkit Token (registration and login):
--------------

**Possible requests:**

    {
        "command": "handle_only_gitkit_token",
        "email_address": "example_user@gmail.com"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true",
    	g_apptoken: "some_token_auto_generated"
    }

Failure (this should never happen):

    {
    	success: "false",
        error: "Unable to generate google user."
        error_code "HOGT_1"
    }


Read Gitkit User Session :
--------------

**Possible requests:**

    {
        "command": "read_gitkit_session_vars",
        "g_apptoken": "some_native_token_only_for_sso",
        "session_keys": [
	        "first_key",
	        "second_key"
	    ]
    }
**Possible responses:**

   Success:
   
    {
    	success: "true",
    	session_vars: {
	    	"some_key": "some_value",
	    	"another_key": "another_value"
    	}
    }

Failure:

    {
    	success: "false",
    	error: "Unknown g_apptoken."
    	error_code: "RGUS_1"
    }

Log Gitkit Users Out:
--------------

**Possible requests:**
 
    {
    	"command": "gitkit_log_out",
    	"g_apptoken": "some_native_token_only_for_sso"
    }

**Possible responses:**

   Success:
   
    {
    	success: "true",
    }

Failure:

    {
    	success: "false",
    	error: "Gitkit user is already logged out."
    	error_code: "LGUO_1"
    }



***Note: In addition to reading Gitkit users sessions, you should be able to set them, so we also have Set and Unset Gitkit Session Vars***

Set Gitkit User Session Variables:
--------------

**Possible requests:**

    {
        "command": "set_session_vars",
        "g_apptoken": "some_g_apptoken",
    	"session_vars": {
	    	"first_key": "first_value",
	    	"second_key": "second_value"
    	}
    }
    
**Possible responses:**

   Success:
   
    {
    	success: "true"
    }

Failure:

    {
    	success: "false",
    	error: "Unknown g_apptoken."
    	error_code: "SGUSV_1"
    }

Unset Session Variables:
--------------

**Possible requests:**

    {
        "command": "unset_session_vars",
        "g_apptoken": "some_g_apptoken",
        "session_keys": [
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
    	error_code: "UGUSV_1"
    }

**All Error Codes:**
================

All error codes are prepended by their command, then followed by a number.

