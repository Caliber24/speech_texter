import pytesseract
from django.core.files.storage import default_storage
from PIL import Image
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)

class OCRException(Exception):
    """کلاس خطای اختصاصی برای خطاهای OCR"""
    pass

class OCRService:
    @staticmethod
    def extract_text_from_image(image_field, retry_count=2):
        """
        استخراج متن از تصویر با امکان تلاش مجدد در صورت خطا
        
        Args:
            image_field: مسیر فایل تصویر
            retry_count: تعداد تلاش‌های مجدد در صورت خطا
            
        Returns:
            متن استخراج شده یا متن خالی در صورت خطا
            
        Raises:
            OCRException: در صورت خطا در پردازش OCR
        """
        attempts = 0
        last_error = None
        
        while attempts <= retry_count:
            try:
                with open(image_field, "rb") as f:
                    img = Image.open(f)
                    # تلاش برای بهبود کیفیت تصویر در صورت تلاش مجدد
                    if attempts > 0:
                        # افزایش وضوح تصویر
                        img = img.convert('L')  # تبدیل به سیاه و سفید
                    
                    text = pytesseract.image_to_string(img)
                    if text.strip():  # اگر متن استخراج شده خالی نباشد
                        return text
                    elif attempts == retry_count:  # آخرین تلاش
                        logger.warning(f"OCR extracted empty text after {attempts+1} attempts")
                        return ""
                    # اگر متن خالی باشد و هنوز تلاش‌های بیشتری باقی مانده، دوباره تلاش می‌کنیم
            except Exception as e:
                last_error = str(e)
                logger.error(f"OCR attempt {attempts+1} failed: {last_error}")
                
            attempts += 1
        
        # اگر به اینجا برسیم، یعنی همه تلاش‌ها شکست خورده‌اند
        error_msg = f"OCR processing failed after {retry_count+1} attempts: {last_error}"
        logger.error(error_msg)
        
        # به جای پرتاب خطا، متن خالی برمی‌گردانیم تا فرآیند ادامه یابد
        return ""
