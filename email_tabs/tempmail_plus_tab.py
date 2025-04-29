import requests
import re
import datetime
from typing import Optional
from .email_tab_interface import EmailTabInterface

class TempMailPlusTab(EmailTabInterface):
    """Implementation of EmailTabInterface for tempmail.plus"""
    
    def __init__(self, email: str, epin: str):
        """Initialize TempMailPlusTab
        
        Args:
            email: The email address to check
            epin: The epin token for authentication
        """
        self.email = email
        self.epin = epin
        self.base_url = "https://tempmail.plus/api"
        self.headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://tempmail.plus/zh/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        self.cookies = {'email': email}
        self._cached_mail_id = None  # 缓存mail_id
        
    def refresh_inbox(self) -> None:
        """Refresh the email inbox"""
        pass
            
    def check_for_cursor_email(self) -> bool:
        """Check if there is a new email within the last 3 minutes
        
        Returns:
            bool: True if new email within 3 minutes exists, False otherwise
        """
        try:
            params = {
                'email': self.email,
                'epin': self.epin
            }
            response = requests.get(
                f"{self.base_url}/mails",
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('result') and data.get('mail_list'):
                current_time = datetime.datetime.now()
                for mail in data['mail_list']:
                    if mail.get('is_new') == True:
                        # 检查邮件时间是否在3分钟内
                        try:
                            mail_time = datetime.datetime.strptime(mail.get('time', ''), '%Y-%m-%d %H:%M:%S')
                            time_diff = (current_time - mail_time).total_seconds() / 60  # 转换为分钟
                            if time_diff <= 3:  # 3分钟内的邮件
                                self._cached_mail_id = mail.get('mail_id')  # 缓存mail_id
                                return True
                        except ValueError:
                            continue
            return False
        except Exception as e:
            print(f"检查新邮件失败: {str(e)}")
            return False
            
    def get_verification_code(self) -> str:
        """Get the verification code from the email
        
        Returns:
            str: The verification code if found, empty string otherwise
        """
        try:
            # 如果没有缓存的mail_id，先检查是否有新邮件
            if not self._cached_mail_id:
                if not self.check_for_cursor_email():
                    return ""
                    
            # 使用缓存的mail_id获取邮件内容
            params = {
                'email': self.email,
                'epin': self.epin
            }
            response = requests.get(
                f"{self.base_url}/mails/{self._cached_mail_id}",
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('result'):
                return ""
                
            # Extract verification code from text content using regex
            text = data.get('text', '')
            match = re.search(r'\n\n(\d{6})\n\n', text)
            if match:
                return match.group(1)
                
            return ""
        except Exception as e:
            print(f"获取验证码失败: {str(e)}")
            return ""

if __name__ == "__main__":
    import os
    import time
    import sys
    
    from config import get_config
    
    config = get_config()
    
    try:
        email = config.get('TempMailPlus', 'email')
        epin = config.get('TempMailPlus', 'epin')
        
        print(f"配置的邮箱: {email}")
        
        # 初始化TempMailPlusTab
        mail_tab = TempMailPlusTab(email, epin)
        
        # 检查是否有Cursor的邮件
        print("正在检查Cursor验证邮件...")
        if mail_tab.check_for_cursor_email():
            print("找到Cursor验证邮件")
            
            # 获取验证码
            verification_code = mail_tab.get_verification_code()
            if verification_code:
                print(f"获取到的验证码: {verification_code}")
            else:
                print("未能获取到验证码")
        else:
            print("未找到Cursor验证邮件")
            
    except configparser.Error as e:
        print(f"读取配置文件错误: {str(e)}")
    except Exception as e:
        print(f"发生错误: {str(e)}") 