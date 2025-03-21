from pdf2image import convert_from_path
import tempfile
import os
from django.conf import settings
import fitz
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import uuid

# تنظیم لاگر
logger = logging.getLogger(__name__)

class PDFException(Exception):
    """کلاس خطای اختصاصی برای خطاهای PDF"""
    pass

class PDFService:
    @staticmethod
    def convert_pdf_to_images(pdf_path, zoom=3, batch_size=5):
        """
        تبدیل PDF به تصویر با PyMuPDF با پشتیبانی از پردازش دسته‌ای
        
        Args:
            pdf_path: مسیر فایل PDF
            zoom: بزرگنمایی تصویر
            batch_size: تعداد صفحات در هر دسته برای پردازش
            
        Returns:
            لیستی از مسیرهای فایل‌های تصویر
            
        Raises:
            PDFException: در صورت خطا در تبدیل PDF
        """
        image_paths = []
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # تقسیم صفحات به دسته‌های کوچکتر برای مدیریت حافظه
            batches = math.ceil(total_pages / batch_size)
            
            logger.info(f"Converting PDF with {total_pages} pages in {batches} batches")
            
            for batch in range(batches):
                start_page = batch * batch_size
                end_page = min((batch + 1) * batch_size, total_pages)
                
                logger.info(f"Processing batch {batch+1}/{batches} (pages {start_page+1}-{end_page})")
                
                # پردازش موازی صفحات در هر دسته
                with ThreadPoolExecutor(max_workers=min(batch_size, os.cpu_count() or 2)) as executor:
                    futures = []
                    
                    for page_num in range(start_page, end_page):
                        futures.append(
                            executor.submit(
                                PDFService._convert_page_to_image, 
                                doc, 
                                page_num, 
                                zoom
                            )
                        )
                    
                    # جمع‌آوری نتایج
                    for future in as_completed(futures):
                        try:
                            img_path = future.result()
                            if img_path:
                                image_paths.append(img_path)
                        except Exception as e:
                            logger.error(f"Error processing page: {str(e)}")
            
            if not image_paths:
                raise PDFException("No images were generated from PDF")
                
            return image_paths
            
        except Exception as e:
            error_msg = f"PDF conversion failed: {str(e)}"
            logger.error(error_msg)
            # به جای پرتاب خطا، لیست خالی برمی‌گردانیم تا فرآیند ادامه یابد
            # اما اگر هیچ تصویری تولید نشده باشد، خطا پرتاب می‌کنیم
            if not image_paths:
                # پاکسازی فایل‌های موقت در صورت وجود
                PDFService._cleanup_temp_files(image_paths)
                raise PDFException(error_msg)
            return image_paths
        except:
            # پاکسازی فایل‌های موقت در صورت بروز هر خطای دیگر
            PDFService._cleanup_temp_files(image_paths)
            raise
    
    @staticmethod
    def _cleanup_temp_files(file_paths):
        """پاکسازی فایل‌های موقت"""
        for path in file_paths:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"Temporary file removed: {path}")
            except Exception as e:
                logger.error(f"Error removing temporary file {path}: {str(e)}")
    
    @staticmethod
    def _convert_page_to_image(doc, page_num, zoom):
        """تبدیل یک صفحه از PDF به تصویر"""
        try:
            # ایجاد یک نام منحصر به فرد با استفاده از UUID
            unique_id = str(uuid.uuid4())
            # استفاده از دایرکتوری موقت سیستم
            temp_dir = tempfile.gettempdir()
            img_filename = f"page_{page_num+1}_{unique_id}.png"
            img_path = os.path.join(temp_dir, img_filename)
            
            page = doc.load_page(page_num)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            pix.save(img_path)
            return img_path
        except Exception as e:
            logger.error(f"Error converting page {page_num+1}: {str(e)}")
            return None
