import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Analysis
from .utils import load_static_result


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
        
        # Start the analysis simulation
        asyncio.create_task(self.simulate_analysis())

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass

    async def simulate_analysis(self):
        """
        Simulate LLM analysis with progress updates.
        In production, this would be replaced with actual LLM processing.
        """
        try:
            # Send initial status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'started',
                'progress': 0,
                'message': 'Analysis started'
            }))
            
            await asyncio.sleep(1)
            
            # Send processing updates
            progress_steps = [
                (20, 'Analyzing packaging image...'),
                (40, 'Processing barcode data...'),
                (60, 'Evaluating market positioning...'),
                (80, 'Generating recommendations...'),
            ]
            
            for progress, message in progress_steps:
                await self.send(text_data=json.dumps({
                    'type': 'status',
                    'status': 'processing',
                    'progress': progress,
                    'message': message
                }))
                await asyncio.sleep(1.5)
            
            # Get the actual analysis data from database
            analysis_data = await self.get_analysis_data()
            
            # Load static result template
            result_data = load_static_result(self.analysis_id)
            
            # Override with actual uploaded data
            if analysis_data:
                result_data['analysis_id'] = str(analysis_data['analysis_id'])
                result_data['barcode'] = analysis_data['barcode']
                result_data['objectives'] = analysis_data['objectives']
                result_data['image_url'] = analysis_data['image_url']
            
            # Update database
            await self.update_analysis_result(result_data)
            
            # Send final result
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'done',
                'progress': 100,
                'message': 'Analysis complete'
            }))
            
            await asyncio.sleep(0.5)
            
            await self.send(text_data=json.dumps({
                'type': 'final_result',
                'payload': result_data
            }))
            
        except Exception as e:
            # Send error status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'error',
                'message': f'Analysis failed: {str(e)}'
            }))
    
    @database_sync_to_async
    def get_analysis_data(self):
        """Get the analysis data from database."""
        try:
            analysis = Analysis.objects.get(analysis_id=self.analysis_id)
            return {
                'analysis_id': analysis.analysis_id,
                'barcode': analysis.barcode,
                'objectives': analysis.objectives,
                'image_url': analysis.image.url if analysis.image else None,
            }
        except Analysis.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_analysis_result(self, result_data):
        """Update the analysis record with results."""
        try:
            analysis = Analysis.objects.get(analysis_id=self.analysis_id)
            analysis.result_data = result_data
            analysis.status = 'completed'
            analysis.save()
        except Analysis.DoesNotExist:
            pass
