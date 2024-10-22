from rest_framework import serializers
from .models import User, Expense, Participant


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['user', 'split_amount', 'splitting_method']


class ExpenseSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'description', 'is_settled', 'created_at', 'updated_at', 'participants']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        user = self.context['request'].user
        expense = Expense.objects.create(user=user, **validated_data)

        for participant_data in participants_data:
            Participant.objects.create(expense=expense, **participant_data)

        return expense

    def validate(self, data):
        # Ensure the total split amount matches the expense amount
        total_split = sum(p['split_amount'] for p in data['participants'])
        if total_split != data['amount']:
            raise serializers.ValidationError("The total split amount must equal the expense amount.")
        return data