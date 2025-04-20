base_mail_template = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="color-scheme" content="dark">
    <meta name="supported-color-schemes" content="dark">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #13161B;
            margin: 0;
            padding: 0;
            color: #e5e7eb;
        }
        .wrapper {
            width: 100%;
            background-color: #13161B;
            padding: 30px 0;
        }
        .content {
            max-width: 600px;
            margin: 0 auto;
            background-color: #22262F;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        .header {
            text-align: center;
            padding: 40px 0 20px;
            background-color: #2a2f3a;
        }
        .header img {
            width: 150px;
            height: 50px;
            max-width: 150px;
        }
        .body {
            padding: 30px 40px;
        }
        .body h1 {
            color: #ba2d0b;
            font-size: 26px;
            margin: 0 0 16px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .body p {
            color: #d1d5db;
            font-size: 15px;
            line-height: 1.7;
            margin: 0 0 16px;
        }
        .body .highlight {
            color: #e5e7eb;
            font-weight: 500;
        }
        .button {
            display: inline-block;
            padding: 14px 28px;
            background: linear-gradient(180deg, #ba2d0b, #9a2509);
            background-color: #ba2d0b;
            color: #ffffff;
            text-decoration: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.2s;
        }
        .button:hover {
            background: #9a2509;
        }
        .divider {
            height: 1px;
            background-color: #374151;
            margin: 24px 0;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background-color: #2a2f3a;
            color: #9ca3af;
            font-size: 13px;
        }
        .footer a {
            color: #ba2d0b;
            text-decoration: underline;
            text-underline-offset: 2px;
        }
        @media (prefers-color-scheme: dark) {
            body, .wrapper {
                background-color: #13161B;
            }
            .content {
                background-color: #22262F;
            }
            .header, .footer {
                background-color: #2a2f3a;
            }
        }
        @media only screen and (max-width: 600px) {
            .content {
                width: 100%;
                margin: 0 12px;
            }
            .body {
                padding: 20px;
            }
            .button {
                display: block;
                text-align: center;
                width: 100%;
                box-sizing: border-box;
            }
            .header img {
                width: 150px;
                height: 100px;
            }
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <table class="content" role="presentation" cellpadding="0" cellspacing="0">
            <tr>
                <td class="header">
                    <a href="{{ APP_FRONT_URL }}">
                        <img src="cid:logo.png" alt="{{ APP_NAME }} logo" title="{{ APP_NAME }} Activation" width="50" height="100">
                    </a>
                </td>
            </tr>
            <tr>
                <td class="body">
                    {% block content %}{% endblock %}
                </td>
            </tr>
            <tr>
                <td class="footer">
                    Powered by <a href="{{ APP_FRONT_URL }}" target="_blank">{{ APP_NAME }}</a>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
"""