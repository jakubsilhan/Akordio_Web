import os, io, shutil
import logging
from app.extensions import get_fullsong_service, get_separation_service
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(ignore_result=False, queue="annotation")
def run_fullsong_task(file_path, model_choice):
    """Celery task for fullsong inference"""
    try:
        # Initialize service
        service = get_fullsong_service()

        # Read bytes
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        # Inference
        results = service.run_inference(audio_bytes, model_choice)
        return results
    except Exception as e:
        logger.error(f"Annotation task failed: {e}", exc_info=True)
        raise e
    finally:
        # Cleanup
        logger.log(0, "Annotation finished")
        if os.path.exists(file_path):
            os.remove(file_path)


@shared_task(ignore_result=False, queue="separation")
def run_separation_task(input_path, output_path, model_choice):
    """Celery task for instrument separation"""
    try:
        # Initialize service
        service = get_separation_service()

        # Read bytes
        with open(input_path, 'rb') as f:
            audio_bytes = f.read()
        audio_buffer = io.BytesIO(audio_bytes)

        # Inference
        result_buffer = service.run_separation(audio_buffer, model_choice)

        # Write audio to temp file
        result_buffer.seek(0)
        with open(output_path, 'wb') as tmp:
            shutil.copyfileobj(result_buffer, tmp)

        return output_path
    except Exception as e:
        logger.error(f"Separation task failed: {e}", exc_info=True)
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e
    finally:
        logger.log(0, "Separation finished")
        if os.path.exists(input_path):
            os.remove(input_path)
