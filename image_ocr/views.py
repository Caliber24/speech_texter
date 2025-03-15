from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.image_serializer import ImageUploadSerializer
from .services.ocr_service import OCRService, OCRException
from .repositories.image_repository import ImageRepository
import os
from .services.pdf_service import PDFService, PDFException
from .serializers.pdf_serializer import PDFUploadSerializer
from tempfile import NamedTemporaryFile
from datetime import datetime
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_datetime
import logging
from django.core.cache import cache
from django.utils.crypto import get_random_string
import time
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# تنظیم لاگر
logger = logging.getLogger(__name__)

# کلاس محدودیت نرخ درخواست برای کاربران ناشناس
class OCRRateThrottle(AnonRateThrottle):
    rate = '10/minute'  # محدودیت 10 درخواست در دقیقه برای کاربران ناشناس

# کلاس محدودیت نرخ درخواست برای کاربران شناسایی شده
class OCRUserRateThrottle(UserRateThrottle):
    rate = '30/minute'  # محدودیت 30 درخواست در دقیقه برای کاربران شناسایی شده


class ImageOCRView(APIView):
    """
    POST:
    دریافت عکس و برگرداندن متن استخراج شده
    """
    throttle_classes = [OCRRateThrottle, OCRUserRateThrottle]

    def post(self, request):
        start_time = time.time()
        request_id = get_random_string(8)  # ایجاد شناسه منحصر به فرد برای درخواست
        logger.info(f"[{request_id}] New image OCR request received")
        
        serializer = ImageUploadSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning(f"[{request_id}] Invalid request data: {serializer.errors}")
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        image_instance = None
        try:
            image_file = serializer.validated_data["image"]
            title = serializer.validated_data["title"]  # اکنون اجباری است
            user_id = serializer.validated_data["user_id"]  # اکنون اجباری است

            # Handle duplicate titles
            title = ImageRepository.get_unique_title(title, user_id)

            # Save image first to ensure we have a record even if OCR fails
            logger.info(f"[{request_id}] Saving image to database for user {user_id}")
            image_instance = ImageRepository.create_image(
                image_file, 
                extracted_text="",
                title=title,
                user_id=user_id
            )
            
            # Process OCR
            logger.info(f"[{request_id}] Starting OCR processing")
            try:
                extracted_text = OCRService.extract_text_from_image(
                    image_instance.image.path
                )
                
                # Update instance with extracted text
                image_instance.extracted_text = extracted_text
                image_instance.save()
                
                processing_time = time.time() - start_time
                logger.info(f"[{request_id}] OCR processing completed in {processing_time:.2f}s")
                
                return Response(
                    {
                        "id": image_instance.id,
                        "text": extracted_text,
                        "image_url": image_instance.image.url,
                        "title": image_instance.title,
                        "created_at": image_instance.created_at,
                        "user_id": image_instance.user_id,
                        "processing_time": f"{processing_time:.2f}s"
                    },
                    status=status.HTTP_201_CREATED,
                )
                
            except OCRException as e:
                # در صورت خطای OCR، تصویر را حفظ می‌کنیم و خطا را گزارش می‌دهیم
                logger.error(f"[{request_id}] OCR processing failed: {str(e)}")
                
                return Response(
                    {
                        "id": image_instance.id,
                        "error": f"OCR processing failed: {str(e)}",
                        "image_url": image_instance.image.url,
                        "title": image_instance.title,
                        "created_at": image_instance.created_at,
                        "user_id": image_instance.user_id,
                        "message": "Image saved successfully but OCR processing failed. You can try again later."
                    },
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )

        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
            
            # اگر تصویر ذخیره شده اما خطای دیگری رخ داده، اطلاعات تصویر را برمی‌گردانیم
            if image_instance:
                return Response(
                    {
                        "id": image_instance.id,
                        "error": f"An error occurred: {str(e)}",
                        "image_url": image_instance.image.url if image_instance.image else None,
                        "title": image_instance.title,
                        "created_at": image_instance.created_at,
                        "user_id": image_instance.user_id,
                        "message": "Image saved but processing failed. You can try again later."
                    },
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )
            else:
                return Response(
                    {"error": f"An error occurred: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


class PDFOCRView(APIView):
    """
    POST:
    دریافت PDF و برگرداندن متن استخراج شده با شماره صفحات
    """
    throttle_classes = [OCRRateThrottle, OCRUserRateThrottle]

    def post(self, request):
        start_time = time.time()
        request_id = get_random_string(8)  # ایجاد شناسه منحصر به فرد برای درخواست
        logger.info(f"[{request_id}] New PDF OCR request received")
        
        serializer = PDFUploadSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning(f"[{request_id}] Invalid request data: {serializer.errors}")
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        pdf_path = None
        image_paths = []
        image_instance = None
        
        try:
            pdf_file = serializer.validated_data["pdf"]
            title = serializer.validated_data["title"]  # اکنون اجباری است
            user_id = serializer.validated_data["user_id"]  # اکنون اجباری است

            # Handle duplicate titles
            title = ImageRepository.get_unique_title(title, user_id)

            # ذخیره موقت PDF
            logger.info(f"[{request_id}] Saving PDF to temporary file")
            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                for chunk in pdf_file.chunks():
                    tmp_pdf.write(chunk)
                pdf_path = tmp_pdf.name

            # ایجاد رکورد در دیتابیس قبل از پردازش OCR
            logger.info(f"[{request_id}] Creating database record for user {user_id}")
            image_instance = ImageRepository.create_image(
                None,  # No image file for PDF
                extracted_text="",
                title=title,
                user_id=user_id
            )

            # تبدیل به عکس
            logger.info(f"[{request_id}] Converting PDF to images")
            try:
                image_paths = PDFService.convert_pdf_to_images(pdf_path)
                
                # پردازش OCR
                logger.info(f"[{request_id}] Starting OCR processing for {len(image_paths)} pages")
                results = []
                combined_text = ""
                successful_pages = 0
                
                for page_num, image_path in enumerate(image_paths, start=1):
                    try:
                        logger.info(f"[{request_id}] Processing page {page_num}")
                        text = OCRService.extract_text_from_image(image_path)
                        results.append({"page": page_num, "text": text.strip()})
                        combined_text += text.strip() + "\n\n"
                        successful_pages += 1
                    except Exception as e:
                        logger.error(f"[{request_id}] Error processing page {page_num}: {str(e)}")
                        results.append({"page": page_num, "text": "", "error": str(e)})
                    finally:
                        # حذف فایل عکس
                        if os.path.exists(image_path):
                            os.remove(image_path)
                
                # Update instance with extracted text
                image_instance.extracted_text = combined_text
                image_instance.save()
                
                processing_time = time.time() - start_time
                logger.info(f"[{request_id}] PDF processing completed in {processing_time:.2f}s. {successful_pages}/{len(image_paths)} pages processed successfully")
                
                # اگر همه صفحات با موفقیت پردازش شده‌اند
                if successful_pages == len(image_paths):
                    return Response({
                        "id": image_instance.id,
                        "pages": results,
                        "title": image_instance.title,
                        "created_at": image_instance.created_at,
                        "user_id": image_instance.user_id,
                        "processing_time": f"{processing_time:.2f}s"
                    }, status=status.HTTP_200_OK)
                else:
                    # اگر برخی صفحات با خطا مواجه شده‌اند
                    return Response({
                        "id": image_instance.id,
                        "pages": results,
                        "title": image_instance.title,
                        "created_at": image_instance.created_at,
                        "user_id": image_instance.user_id,
                        "processing_time": f"{processing_time:.2f}s",
                        "message": f"{successful_pages} of {len(image_paths)} pages processed successfully"
                    }, status=status.HTTP_206_PARTIAL_CONTENT)
                
            except PDFException as e:
                # در صورت خطای PDF، رکورد را حفظ می‌کنیم و خطا را گزارش می‌دهیم
                logger.error(f"[{request_id}] PDF processing failed: {str(e)}")
                
                return Response(
                    {
                        "id": image_instance.id,
                        "error": f"PDF processing failed: {str(e)}",
                        "title": image_instance.title,
                        "created_at": image_instance.created_at,
                        "user_id": image_instance.user_id,
                        "message": "PDF record saved but processing failed. You can try again later."
                    },
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )

        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
            
            # اگر رکورد ایجاد شده اما خطای دیگری رخ داده، اطلاعات رکورد را برمی‌گردانیم
            if image_instance:
                return Response(
                    {
                        "id": image_instance.id,
                        "error": f"An error occurred: {str(e)}",
                        "title": image_instance.title,
                        "created_at": image_instance.created_at,
                        "user_id": image_instance.user_id,
                        "message": "PDF record saved but processing failed. You can try again later."
                    },
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )
            else:
                return Response(
                    {"error": f"An error occurred: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
                
        finally:
            # حذف فایل‌های باقیمانده
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
            for path in image_paths:
                if os.path.exists(path):
                    os.remove(path)


class UserPostsView(APIView):
    """
    GET:
    دریافت پست‌های کاربر بعد از یک تاریخ مشخص با استفاده از Unix timestamp
    """
    throttle_classes = [OCRRateThrottle, OCRUserRateThrottle]
    
    def get(self, request):
        request_id = get_random_string(8)
        logger.info(f"[{request_id}] New user posts request received")
        
        user_id = request.query_params.get('user_id')
        unix_timestamp = request.query_params.get('timestamp')
        
        if not user_id:
            logger.warning(f"[{request_id}] Missing user_id parameter")
            return Response(
                {"error": "user_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not unix_timestamp:
            logger.warning(f"[{request_id}] Missing timestamp parameter")
            return Response(
                {"error": "timestamp is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Convert Unix timestamp to datetime
            try:
                unix_timestamp = int(unix_timestamp)
                timestamp = datetime.fromtimestamp(unix_timestamp)
            except ValueError:
                logger.warning(f"[{request_id}] Invalid timestamp format: {unix_timestamp}")
                return Response(
                    {"error": "Invalid timestamp format. Use Unix timestamp (seconds since epoch)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Get posts after timestamp
            logger.info(f"[{request_id}] Retrieving posts for user {user_id} after {timestamp}")
            posts = ImageRepository.get_user_posts_after_timestamp(user_id, timestamp)
            
            # Serialize the results
            results = []
            for post in posts:
                # Convert datetime to Unix timestamp for response
                created_at_unix = int(post.created_at.timestamp())
                
                results.append({
                    "id": post.id,
                    "title": post.title,
                    "extracted_text": post.extracted_text,
                    "created_at": created_at_unix,  # Return as Unix timestamp
                    "image_url": post.image.url if post.image else None
                })
                
            logger.info(f"[{request_id}] Found {len(results)} posts")
            return Response(
                {"posts": results},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"[{request_id}] Error retrieving user posts: {str(e)}", exc_info=True)
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
