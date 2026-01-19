import json
import base64
import logging
from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Student, AttendanceRecord, FaceEncoding
from .face_utils import face_recognizer, FaceDetectionError

logger = logging.getLogger(__name__)

# ------------------ Face Detection & Attendance Views ------------------

@csrf_exempt
def save_face_encoding(request):
    """API endpoint to save face encoding during student registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            face_image_base64 = data.get('face_image')
            
            if not student_id or not face_image_base64:
                return JsonResponse({
                    'success': False,
                    'message': 'Missing student_id or face_image'
                }, status=400)
            
            # Get student
            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Student not found'
                }, status=404)
            
            # Convert base64 to image
            image = face_recognizer.base64_to_image(face_image_base64)
            
            # Verify face quality
            success, message, faces = face_recognizer.verify_face_quality(image)
            if not success:
                return JsonResponse({
                    'success': False,
                    'message': message
                }, status=400)
            
            # Get the first detected face (for registration, should be only one)
            face_rect = faces[0]
            
            # Generate face encoding
            encoding = face_recognizer.encode_face(image, face_rect)
            
            # Save face image
            image_path = face_recognizer.save_face_image(image, student_id, face_rect)
            
            # Save to database
            FaceEncoding.objects.create(
                student=student,
                encoding_data=json.dumps(encoding),
                image_path=image_path,
                is_active=True
            )
            
            # Update student training status AND photo
            student.is_trained = True
            # Set the main photo to this new image if not set, or update it
            if not student.photo:
                student.photo = image_path
            student.save()
            
            # Refresh in-memory cache so new student is recognizable immediately
            face_recognizer.refresh_encodings()
            
            return JsonResponse({
                'success': True,
                'message': 'Face registered successfully!',
                'image_path': image_path
            })
            
        except FaceDetectionError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def mark_attendance_view(request):
    """Page for marking attendance using face recognition"""
    # Get today's attendance summary
    today = date.today()
    total_students = Student.objects.filter(is_trained=True).count()
    present_today = AttendanceRecord.objects.filter(date=today, status='present').count()
    
    context = {
        'total_students': total_students,
        'present_today': present_today,
        'absent_today': total_students - present_today,
        'today': today
    }
    
    return render(request, 'dashboard/mark_attendance.html', context)


@csrf_exempt
def process_attendance(request):
    """API endpoint to process face recognition for attendance (supports multiple faces)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            face_image_base64 = data.get('face_image')
            
            if not face_image_base64:
                return JsonResponse({
                    'success': False,
                    'message': 'No face image provided'
                }, status=400)
            
            # Convert base64 to image
            image = face_recognizer.base64_to_image(face_image_base64)
            
            # Recognize faces
            try:
                # This will use the cache automatically (loaded on startup)
                results = face_recognizer.recognize_faces(image)
            except FaceDetectionError as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            
            if not results:
                return JsonResponse({
                    'success': False,
                    'message': 'No faces detected. Please ensure your face is visible and well-lit.',
                    'face_count': 0
                }, status=200)
            
            processed_students = []
            all_face_rects = []  # For visual feedback
            
            for result in results:
                student_id = result['student_id']
                confidence = result['confidence']
                face_rect = result['rect']
                
                # Add face rectangle for visual feedback (even for unrecognized faces)
                all_face_rects.append({
                    'x': face_rect[0],
                    'y': face_rect[1],
                    'w': face_rect[2],
                    'h': face_rect[3],
                    'recognized': student_id is not None,
                    'confidence': confidence
                })
                
                if student_id is None:
                    continue  # Skip unrecognized faces for attendance
                
                # Get student
                try:
                    student = Student.objects.get(student_id=student_id)
                except Student.DoesNotExist:
                    continue
                
                # Check if already marked today
                today = date.today()
                
                # Prevent duplicates
                # Optionally add tracking for rapid re-marking prevention in session
                
                attendance, created = AttendanceRecord.objects.get_or_create(
                    student=student,
                    date=today,
                    defaults={
                        'status': 'present',
                        'marked_by_face': True,
                        'confidence_score': confidence
                    }
                )
                
                student_data = {
                    'name': student.name,
                    'student_id': student.student_id,
                    'class_year': student.class_year,
                    'confidence': confidence,
                    'face_rect': {
                        'x': face_rect[0],
                        'y': face_rect[1],
                        'w': face_rect[2],
                        'h': face_rect[3]
                    },
                    'status': 'marked' if created else 'already_marked',
                    'time': attendance.time.strftime("%H:%M:%S") if hasattr(attendance, 'time') else "Now"
                }
                
                processed_students.append(student_data)
            
            if not processed_students:
                return JsonResponse({
                    'success': False,
                    'message': f'Detected {len(results)} face(s), but none matched registered students.',
                    'face_count': len(results),
                    'face_rects': all_face_rects,
                    'results': results,  # DEBUG INFO
                    'detection_model': face_recognizer.detection_model
                }, status=200)
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully identified {len(processed_students)} student(s).',
                'results': processed_students,
                'face_count': len(results),
                'face_rects': all_face_rects,
                'detection_model': face_recognizer.detection_model
            })
            
        except Exception as e:
            import traceback
            logger.error(f"Attendance processing error: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def attendance_history(request):
    """View attendance history with filters"""
    # Get filter parameters
    search_query = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')
    class_filter = request.GET.get('class', '')
    
    # Base queryset
    records = AttendanceRecord.objects.select_related('student').all()
    
    # Apply filters
    if search_query:
        records = records.filter(
            Q(student__name__icontains=search_query) |
            Q(student__student_id__icontains=search_query)
        )
    
    if date_filter:
        records = records.filter(date=date_filter)
    
    if class_filter:
        records = records.filter(student__class_year=class_filter)
    
    # Get statistics
    total_records = records.count()
    present_count = records.filter(status='present').count()
    absent_count = records.filter(status='absent').count()
    
    context = {
        'records': records[:100],  # Limit to 100 recent records
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'search_query': search_query,
        'date_filter': date_filter,
        'class_filter': class_filter,
    }
    
    return render(request, 'dashboard/attendance_history.html', context)
