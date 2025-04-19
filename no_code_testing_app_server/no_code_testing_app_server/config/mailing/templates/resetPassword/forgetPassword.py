import os

SKY_FORGE_APP_URL = os.environ['APP_FRONT_URL']


head = """<!DOCTYPE html>
<html>

<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="color-scheme" content="light">
    <meta name="supported-color-schemes" content="light">
    <style>
        @media only screen and (max-width: 600px) {
            .inner-body {
                width: 100% !important;
            }

            .footer {
                width: 100% !important;
            }
        }

        @media only screen and (max-width: 500px) {
            .button {
                width:
                    100% !important;
            }
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
        }
    </style>
</head>
                    """

body = """
               
<body
    style="box-sizing: border-box; position: relative; -webkit-text-size-adjust: none; background-color: #ffffff; color: #718096; height: 100%; line-height: 1.4; margin: 0; padding: 0; width: 100% !important;">
    <table class="wrapper" width="100%" cellpadding="0" cellspacing="0" role="presentation"
        style="box-sizing: border-box;position: relative; margin: 0; padding: 0; width: 100%;">
        <tr>
            <td style="box-sizing: border-box; position: relative;">
                <table class="content" width="100%" cellpadding="0" cellspacing="0" role="presentation"
                    style="box-sizing: border-box; position: relative;margin: 0; padding: 0; width: 100%;">
                    <tr>
                        <td class="header"
                            style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont,'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; padding: 25px 0; text-align: center;">
                            <a href="{SKY_FORGE_APP_URL}"
                                style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'SegoeUI Emoji', 'Segoe UI Symbol'; position: relative; color: #4852; font-size: 19px; font-weight: bold; text-decoration: none; display: inline-block;">
                                <img src="cid:logo.png" alt="sky forge logo"
                                    style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; border: none; max-width: 180px; margin: auto;"
                                    title="SpinBooth-UM Activation"></a>
                        </td>
                    </tr>

                    <!-- Email Body -->
                    <tr>
                        <td class="body" width="100%" cellpadding="0" cellspacing="0"
                            style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; -premailer-cellpadding: 0; -premailer-cellspacing: 0; -premailer-width: 100%; background-color: #edf2f7; border-bottom: 1px solid #edf2f7; border-top: 1px solid #edf2f7; margin: 0; padding: 0; width: 100%;">
                            <table class="inner-body" width="570" cellpadding="0" cellspacing="0" role="presentation"
                                style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont,'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; -premailer-cellpadding: 0; -premailer-cellspacing: 0; -premailer-width: 570px; background-color:#ffffff; border-color: #e8e5ef; border-radius: 2px; border-width: 1px; box-shadow: 0 2px 0 rgba(0, 0, 150, 0.025), 2px 4px 0 rgba(0, 0, 150, 0.015); margin: 0 auto; padding: 0; width: 570px;">
                                <!-- Body content -->
                                <tr>
                                    <td class="content-cell"
                                        style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; max-width: 100vw; padding: 32px;">
                                        <h1
                                            style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; color:  rgb(0, 146, 212); font-size: 18px; font-weight: bold; margin-top: 0; text-align: left;">
                                            Hello {first_name}!</h1>
                                        <p
                                            style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont,'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; font-size: 16px; line-height: 1.5em; margin-top: 0; text-align: left;">
                                            Someone has requested a link to reset your password. If you requested this,
                                            you can change your password through the button below.</p>
                                        <div
                                            style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position:relative; text-align: center; margin-bottom: 20px;">
                                            <strong
                                                style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative;"></strong>
                                        </div>
                                        <p
                                            style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; font-size: 16px; line-height: 1.5em; margin-top: 0; text-align: left;">
                                            <a style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; display: block; padding: 0.5rem; text-decoration:none; max-width: 200px; text-align: center; margin: auto; border-radius: 4px; white-space: nowrap; background: #2D3748; color: #ffffff;"
                                                href="{link}" target="_blank">Reset Password</a>
                                        <p
                                            style="box-sizing: border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; font-size: 16px; line-height: 1.5em; margin-top: 0; text-align: left;">
                                            Your password won't change until you access the link above and create a new
                                            one.</p>
                                        </p>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>
                    <tr>
                        <td
                            style="box-sizing: border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative;">
                            <table class="footer" width="570" cellpadding="0" cellspacing="0" role="presentation"
                                style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji','Segoe UI Symbol'; position: relative; -premailer-cellpadding: 0; -premailer-cellspacing: 0; -premailer-width: 570px; margin: 0 auto; padding: 0; text-align: center; width: 570px;">
                                <tr>
                                    <td class="content-cell"
                                        style="box-sizing: border-box; font-family: -apple-system, BlinkM=acSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Colo=r Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; max-width: 100vw; padding: 32px;">

                                        <div style="box-sizing: border-box; position: relative; padding: .5rem;">
                                            <span
                                                style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Aria=l, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; position: relative;">Powered
                                                By </span><a href=""
                                                style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemF=ont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji','Segoe UI Emoji', 'Segoe UI Symbol'; position: relative; color: #b0adc5; text-decoration: underline; display: block; text-align: center;"
                                                target="_blank">Sky forge.</a>
                                        </div>

                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>

</html>"""


def prepare_core(**Kwargs):
    formate_body = body.format(**Kwargs, SKY_FORGE_APP_URL=SKY_FORGE_APP_URL)
    return head + formate_body


def get_email(receiver, *args, **kwargs):
    first_name = kwargs['first_name']
    reset_token = kwargs['reset_token']
    return {
        'FromEmail': os.environ['MAIL_JET_FROM_EMAIL'],
        'FromName': 'No code app support',
        'Subject': 'Reset password',
        'Html-part': f'{prepare_core(first_name = first_name,link=SKY_FORGE_APP_URL+"/forget/password/"+reset_token)}',
        'Recipients': [{'Email': f'{receiver}'}],
    }
