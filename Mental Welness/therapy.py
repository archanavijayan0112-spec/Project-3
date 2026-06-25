from flask import Flask, render_template, request, jsonify

"""
Mental Health Therapist Suggestion Application

This module provides therapist recommendation functionality for mental health wellness applications.
"""

class Therapist:
    """
    Class representing a mental health therapist.
    """
    def __init__(self, id, name, specializations, location, availability, approach, 
                 experience, insurance_accepted, contact, bio):
        self.id = id
        self.name = name
        self.specializations = specializations
        self.location = location
        self.availability = availability
        self.approach = approach
        self.experience = experience
        self.insurance_accepted = insurance_accepted
        self.contact = contact
        self.bio = bio
    
    def to_dict(self):
        """Convert therapist object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'specializations': self.specializations,
            'location': self.location,
            'availability': self.availability,
            'approach': self.approach,
            'experience': self.experience,
            'insurance_accepted': self.insurance_accepted,
            'contact': self.contact,
            'bio': self.bio
        }


class TherapistDatabase:
    """
    Class to manage a database of therapists and provide search functionality.
    """
    def __init__(self):
        self.therapists = []
        self._load_sample_data()
    
    def _load_sample_data(self):
        """
        Load sample therapist data.
        """
        # Sample therapist data
        self.therapists = [
            Therapist(
                id=1,
                name="Dr. Sarah Johnson",
                specializations=["Anxiety", "Depression", "Trauma"],
                location="New York, NY",
                availability="Mon-Fri, 9am-5pm",
                approach="Cognitive Behavioral Therapy (CBT)",
                experience=15,
                insurance_accepted=["Blue Cross", "Aetna", "UnitedHealthcare"],
                contact="dr.johnson@example.com",
                bio="Dr. Johnson specializes in helping adults overcome anxiety and depression through evidence-based approaches."
            ),
            Therapist(
                id=2,
                name="Dr. Michael Chen",
                specializations=["ADHD", "Family Therapy", "Child Psychology"],
                location="San Francisco, CA",
                availability="Tue-Sat, 10am-6pm",
                approach="Family Systems Therapy",
                experience=10,
                insurance_accepted=["Kaiser", "Cigna", "Medicare"],
                contact="dr.chen@example.com",
                bio="Dr. Chen works with children, adolescents, and families to address behavioral and emotional challenges."
            ),
            Therapist(
                id=3,
                name="Dr. Emily Rodriguez",
                specializations=["PTSD", "Grief Counseling", "Mindfulness"],
                location="Chicago, IL",
                availability="Mon-Thu, 8am-8pm",
                approach="Mindfulness-Based Stress Reduction (MBSR)",
                experience=8,
                insurance_accepted=["Humana", "Blue Shield", "Medicaid"],
                contact="dr.rodriguez@example.com",
                bio="Dr. Rodriguez integrates mindfulness practices with therapeutic techniques to help clients cope with trauma and loss."
            ),
            Therapist(
                id=4,
                name="Dr. James Wilson",
                specializations=["Substance Abuse", "Addiction Recovery", "Dual Diagnosis"],
                location="Austin, TX",
                availability="Wed-Sun, 11am-7pm",
                approach="Motivational Interviewing",
                experience=12,
                insurance_accepted=["Anthem", "UnitedHealthcare", "Cigna"],
                contact="dr.wilson@example.com",
                bio="Dr. Wilson has extensive experience helping individuals overcome addiction and substance abuse issues."
            ),
            Therapist(
                id=5,
                name="Dr. Amara Patel",
                specializations=["Relationship Issues", "Cultural Identity", "LGBTQ+ Support"],
                location="Seattle, WA",
                availability="Mon-Wed & Fri, 9am-6pm",
                approach="Psychodynamic Therapy",
                experience=9,
                insurance_accepted=["Premera", "Regence", "Aetna"],
                contact="dr.patel@example.com",
                bio="Dr. Patel creates a safe space for exploring relationship dynamics and cultural identities."
            )
        ]
    
    def get_all_therapists(self):
        """
        Return all therapists in the database.
        """
        return self.therapists
    
    def get_therapist_by_id(self, id):
        """
        Find a therapist by their ID.
        """
        for therapist in self.therapists:
            if therapist.id == id:
                return therapist
        return None
    
    def search_by_specialization(self, specialization):
        """
        Find therapists by specialization.
        """
        results = []
        if not specialization:
            return self.therapists
            
        for therapist in self.therapists:
            if specialization.lower() in [s.lower() for s in therapist.specializations]:
                results.append(therapist)
        return results
    
    def search_by_location(self, location):
        """
        Find therapists by location.
        """
        results = []
        if not location:
            return self.therapists
            
        for therapist in self.therapists:
            if location.lower() in therapist.location.lower():
                results.append(therapist)
        return results
    
    def search_by_insurance(self, insurance):
        """
        Find therapists who accept a specific insurance.
        """
        results = []
        if not insurance:
            return self.therapists
            
        for therapist in self.therapists:
            if insurance.lower() in [i.lower() for i in therapist.insurance_accepted]:
                results.append(therapist)
        return results

    def get_therapist_recommendation(self, issue=None, location=None, insurance=None):
        """
        Get therapist recommendations based on multiple criteria.
        """
        candidates = self.therapists.copy()
        
        if issue:
            filtered = []
            for therapist in candidates:
                for specialization in therapist.specializations:
                    if issue.lower() in specialization.lower():
                        filtered.append(therapist)
                        break
            candidates = filtered
        
        if location and candidates:
            filtered = []
            for therapist in candidates:
                if location.lower() in therapist.location.lower():
                    filtered.append(therapist)
            candidates = filtered
        
        if insurance and candidates:
            filtered = []
            for therapist in candidates:
                if insurance.lower() in [i.lower() for i in therapist.insurance_accepted]:
                    filtered.append(therapist)
            candidates = filtered
        
        return candidates

