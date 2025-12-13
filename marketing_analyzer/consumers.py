import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Analysis
from .fastapi_client import FastAPIClient

logger = logging.getLogger(__name__)


class AnalysisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.analysis_id = self.scope['url_route']['kwargs']['analysis_id']
        self.room_group_name = f'analysis_{self.analysis_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Start the analysis
        asyncio.create_task(self.run_analysis())

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass

    async def run_analysis(self):
        """
        Run LLM analysis by calling FastAPI service.
        FastAPI handles:
        - Product lookup from OpenFoodFacts
        - Image extraction (image_front_url)
        - LLM analysis
        - Complete JSON response
        """
        try:
            # Send initial status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'started',
                'progress': 0,
                'message': 'Analysis started'
            }))
            
            # Get analysis data from database
            analysis_data = await self.get_analysis_data()
            if not analysis_data:
                await self.send_error("Analysis record not found")
                return
            
            # Update status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'processing',
                'progress': 20,
                'message': 'Connecting to analysis service...'
            }))
            
            # Initialize FastAPI client
            client = FastAPIClient()
            
            # Call FastAPI /run-analysis endpoint
            # FastAPI will handle:
            # 1. OpenFoodFacts lookup
            # 2. Image extraction
            # 3. LLM analysis
            # 4. Return complete JSON
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'processing',
                'progress': 40,
                'message': 'Analyzing product packaging and market positioning...'
            }))
            
            success, result = await asyncio.to_thread(
                client.run_analysis,
                analysis_data['analysis_id'],
                analysis_data['barcode'],
                analysis_data['objectives']
            )
            
            if not success:
                # result contains error message
                await self.send_error(result)
                await self.update_analysis_error(result)
                return
            
            # Analysis successful
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'processing',
                'progress': 90,
                'message': 'Finalizing recommendations...'
            }))
            
            # Save results to database
            await self.update_analysis_result(result)
            
            # Send completion status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'done',
                'progress': 100,
                'message': 'Analysis complete'
            }))
            
            await asyncio.sleep(0.3)
            
            # Send final result
            await self.send(text_data=json.dumps({
                'type': 'final_result',
                'payload': result
            }))
            
        except Exception as e:
            logger.exception(f"Unexpected error in analysis {self.analysis_id}")
            await self.send_error("An unexpected error occurred. Please try again.")
            await self.update_analysis_error(str(e))
    
    async def send_error(self, error_message):
        """Send user-friendly error message via WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'status',
            'status': 'error',
            'message': error_message
        }))
    
    @database_sync_to_async
    def get_analysis_data(self):
        """Get the analysis data from database."""
        try:
            analysis = Analysis.objects.get(analysis_id=self.analysis_id)
            return {
                'analysis_id': str(analysis.analysis_id),
                'barcode': analysis.barcode,
                'objectives': analysis.objectives,
            }
        except Analysis.DoesNotExist:
            logger.error(f"Analysis not found: {self.analysis_id}")
            return None
    
    @database_sync_to_async
    def update_analysis_result(self, result_data):
        """Update the analysis record with results."""
        try:
            analysis = Analysis.objects.get(analysis_id=self.analysis_id)
            analysis.result_data = result_data
            analysis.status = 'completed'
            analysis.error_message = None
            analysis.save()
            logger.info(f"Analysis completed successfully: {self.analysis_id}")
        except Analysis.DoesNotExist:
            logger.error(f"Analysis not found for update: {self.analysis_id}")
    
    @database_sync_to_async
    def update_analysis_error(self, error_message):
        """Update the analysis record with error."""
        try:
            analysis = Analysis.objects.get(analysis_id=self.analysis_id)
            analysis.status = 'error'
            analysis.error_message = error_message
            analysis.save()
            logger.error(f"Analysis failed: {self.analysis_id} - {error_message}")
        except Analysis.DoesNotExist:
            logger.error(f"Analysis not found for error update: {self.analysis_id}")
