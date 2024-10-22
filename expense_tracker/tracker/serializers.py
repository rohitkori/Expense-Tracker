from rest_framework import serializers
from .models import User, Expense, Participant
from decimal import Decimal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    split_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)

    class Meta:
        model = Participant
        fields = ['user', 'split_amount', 'percentage']

class ExpenseSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True)
    splitting_method = serializers.ChoiceField(choices=['EQUAL', 'EXACT', 'PERCENTAGE'])

    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'description', 'splitting_method', 'is_settled', 'created_at', 'updated_at', 'participants']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        user = self.context['request'].user
        expense = Expense.objects.create(user=user, **validated_data)
        splitting_method = validated_data['splitting_method']

        if splitting_method == 'EQUAL':
            split_amount = validated_data['amount'] / len(participants_data)
            for participant_data in participants_data:
                participant_data['split_amount'] = split_amount
                Participant.objects.create(expense=expense, **participant_data)
        
        elif splitting_method == 'PERCENTAGE':
            total_percentage = sum(Decimal(p.get('percentage', 0)) for p in participants_data)
            if total_percentage != 100:
                raise serializers.ValidationError("The total percentage must equal 100%.")
            for participant_data in participants_data:
                percentage = Decimal(participant_data.get('percentage', 0))
                participant_data['split_amount'] = (percentage / 100) * validated_data['amount']
                participant_data.pop('percentage')
                Participant.objects.create(expense=expense, **participant_data)
            
        else:  # EXACT
            total_split = sum(Decimal(p['split_amount']) for p in participants_data)
            if total_split != validated_data['amount']:
                raise serializers.ValidationError("The total split amount must equal the expense amount.")
            for participant_data in participants_data:
                Participant.objects.create(expense=expense, **participant_data)

        return expense

    def validate(self, data):
        splitting_method = data['splitting_method']
        participants = data['participants']
        amount = Decimal(data['amount'])

        if splitting_method == 'EQUAL':
            split_amount = amount / len(participants)
            for participant in participants:
                participant['split_amount'] = split_amount

        elif splitting_method == 'PERCENTAGE':
            total_percentage = sum(Decimal(p.get('percentage', 0)) for p in participants)
            if total_percentage != 100:
                raise serializers.ValidationError("The total percentage must equal 100%.")
            for participant in participants:
                percentage = Decimal(participant.get('percentage', 0))
                participant['split_amount'] = (percentage / 100) * amount
        else :
            total_split = sum(Decimal(p['split_amount']) for p in participants)
            if total_split != amount:
                raise serializers.ValidationError("The total split amount must equal the expense amount.")

        return data
