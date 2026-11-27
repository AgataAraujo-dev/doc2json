import os


class BedrockLLM:
    def __init__(self, model_id: str | None = None, region: str | None = None):
        import boto3

        self.model_id = model_id or os.environ.get('BEDROCK_MODEL_ID')
        if not self.model_id:
            raise ValueError('Defina a variável de ambiente BEDROCK_MODEL_ID.')

        self.client = boto3.client(
            'bedrock-runtime',
            region_name=region or os.environ.get('AWS_REGION', 'us-east-1'),
        )

    def complete(self, prompt: str) -> str:
        resposta = self.client.converse(
            modelId=self.model_id,
            messages=[{'role': 'user', 'content': [{'text': prompt}]}],
            inferenceConfig={'maxTokens': 2000, 'temperature': 0},
        )
        return resposta['output']['message']['content'][0]['text']
