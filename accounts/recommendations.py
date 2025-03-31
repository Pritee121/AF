
# # # # from collections import defaultdict, Counter
# # # # from decimal import Decimal
# # # # import numpy as np
# # # # from .models import Booking, Service

# # # # def recommend_services_ai_price_band(user):
# # # #     completed_bookings = Booking.objects.filter(client=user, status="Completed")
# # # #     print("\n✅ Completed Bookings:", completed_bookings.count())

# # # #     if completed_bookings.count() < 1:
# # # #         return []

# # # #     booked_services = completed_bookings.values_list('service__service_name', 'service__price')

# # # #     booked_price_bands = []
# # # #     booked_prices = []

# # # #     # Step 1: Group all services by name
# # # #     services_by_name = defaultdict(list)
# # # #     for s in Service.objects.all():
# # # #         services_by_name[s.service_name].append(s)

# # # #     print("\n📊 All Service Prices by Name:")
# # # #     for name, services in services_by_name.items():
# # # #         prices = [float(s.price) for s in services]
# # # #         print(f"  {name}: {prices}")

# # # #     for service_name, booked_price in booked_services:
# # # #         booked_prices.append(float(booked_price))
# # # #         related_services = services_by_name[service_name]

# # # #         if len(related_services) < 3:
# # # #             continue  # Not enough data to band

# # # #         all_prices = sorted([float(s.price) for s in related_services])
# # # #         p33 = np.percentile(all_prices, 33)
# # # #         p66 = np.percentile(all_prices, 66)

# # # #         if float(booked_price) <= p33:
# # # #             booked_price_bands.append((service_name, 'low'))
# # # #         elif float(booked_price) <= p66:
# # # #             booked_price_bands.append((service_name, 'medium'))
# # # #         else:
# # # #             booked_price_bands.append((service_name, 'high'))

# # # #         print(f"\n🎯 {service_name} | Booked: {booked_price} | P33: {p33}, P66: {p66} => Band: {booked_price_bands[-1][1]}")

# # # #     # Step 2: Count the most frequent band across all booked services
# # # #     band_counts = Counter([band for _, band in booked_price_bands])
# # # #     if not band_counts:
# # # #         return []

# # # #     most_common_band = band_counts.most_common(1)[0][0]
# # # #     print(f"\n🏆 Most Frequent Band Overall: {most_common_band}")

# # # #     # Step 3: Recommend services from all categories matching the most common band
# # # #     recommendations = []
# # # #     for service_name, related_services in services_by_name.items():
# # # #         if len(related_services) < 3:
# # # #             continue

# # # #         all_prices = sorted([float(s.price) for s in related_services])
# # # #         p33 = np.percentile(all_prices, 33)
# # # #         p66 = np.percentile(all_prices, 66)

# # # #         for service in related_services:
# # # #             price = float(service.price)
# # # #             band = 'low' if price <= p33 else 'medium' if price <= p66 else 'high'

# # # #             if band == most_common_band:
# # # #                 recommendations.append(service)

# # # #         print(f"\n🔍 {service_name}: Matching Band = {most_common_band} => Total Matching: {len([s for s in related_services if (float(s.price) <= p33 and most_common_band == 'low') or (p33 < float(s.price) <= p66 and most_common_band == 'medium') or (float(s.price) > p66 and most_common_band == 'high')])}")

# # # #     print("\n✅ Final Recommended Services:", [s.service_name for s in recommendations])
# # # #     return recommendations


# # # from collections import defaultdict, Counter
# # # from decimal import Decimal
# # # import numpy as np
# # # from sentence_transformers import SentenceTransformer, util
# # # from .models import Booking, Service

# # # # Load sentence transformer model (can be loaded globally)
# # # model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# # # def recommend_services_ai_price_band(user):
# # #     completed_bookings = Booking.objects.filter(client=user, status="Completed")
# # #     print("\n✅ Completed Bookings:", completed_bookings.count())

# # #     if completed_bookings.count() < 1:
# # #         return []

# # #     booked_services = list(completed_bookings.values_list('service__service_name', 'service__price', 'service__description'))

# # #     booked_price_bands = []
# # #     booked_prices = []
# # #     booked_descriptions = []

# # #     # Step 1: Group all services by name
# # #     services_by_name = defaultdict(list)
# # #     for s in Service.objects.all():
# # #         services_by_name[s.service_name].append(s)

# # #     print("\n📊 All Service Prices by Name:")
# # #     for name, services in services_by_name.items():
# # #         prices = [float(s.price) for s in services]
# # #         print(f"  {name}: {prices}")

# # #     for service_name, booked_price, description in booked_services:
# # #         booked_prices.append(float(booked_price))
# # #         if description:
# # #             booked_descriptions.append(description)

# # #         related_services = services_by_name[service_name]
# # #         if len(related_services) < 3:
# # #             continue  # Not enough data to band

# # #         all_prices = sorted([float(s.price) for s in related_services])
# # #         p33 = np.percentile(all_prices, 33)
# # #         p66 = np.percentile(all_prices, 66)

# # #         if float(booked_price) <= p33:
# # #             booked_price_bands.append((service_name, 'low'))
# # #         elif float(booked_price) <= p66:
# # #             booked_price_bands.append((service_name, 'medium'))
# # #         else:
# # #             booked_price_bands.append((service_name, 'high'))

# # #         print(f"\n🎯 {service_name} | Booked: {booked_price} | P33: {p33}, P66: {p66} => Band: {booked_price_bands[-1][1]}")

# # #     # Step 2: Count most frequent band
# # #     band_counts = Counter([band for _, band in booked_price_bands])
# # #     if not band_counts:
# # #         return []

# # #     most_common_band = band_counts.most_common(1)[0][0]
# # #     print(f"\n🏆 Most Frequent Band Overall: {most_common_band}")

# # #     # Step 3: AI-based filtering using service description
# # #     recommendations = []
# # #     all_services = list(Service.objects.exclude(description=""))
# # #     all_descriptions = [s.description for s in all_services]

# # #     if booked_descriptions and all_descriptions:
# # #         user_embedding = model.encode(booked_descriptions, convert_to_tensor=True).mean(dim=0)
# # #         all_embeddings = model.encode(all_descriptions, convert_to_tensor=True)

# # #         cos_scores = util.cos_sim(user_embedding, all_embeddings)[0].cpu().numpy()
# # #         sorted_indices = np.argsort(-cos_scores)[:20]  # top 20

# # #         for idx in sorted_indices:
# # #             s = all_services[int(idx)]  # Ensure idx is an int, not a Tensor
# # #             if not Booking.objects.filter(client=user, service=s, status="Completed").exists():
# # #                 recommendations.append(s)

# # #     # Step 4: Filter only those that match most common band for each service name
# # #     final_recommendations = []
# # #     for service in recommendations:
# # #         group = services_by_name[service.service_name]
# # #         if len(group) < 3:
# # #             continue

# # #         prices = sorted([float(s.price) for s in group])
# # #         p33 = np.percentile(prices, 33)
# # #         p66 = np.percentile(prices, 66)

# # #         price = float(service.price)
# # #         band = 'low' if price <= p33 else 'medium' if price <= p66 else 'high'

# # #         if band == most_common_band:
# # #             final_recommendations.append(service)

# # #     print("\n✅ Final Recommended Services:", [s.service_name for s in final_recommendations])
# # #     return final_recommendations
# # from collections import defaultdict, Counter
# # from decimal import Decimal
# # import numpy as np
# # from sentence_transformers import SentenceTransformer, util
# # from .models import Booking, Service

# # # Load sentence transformer model (can be loaded globally)
# # model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# # def recommend_services_ai_price_band(user):
# #     completed_bookings = Booking.objects.filter(client=user, status="Completed")
# #     print("\n✅ Completed Bookings:", completed_bookings.count())

# #     if completed_bookings.count() < 1:
# #         return []

# #     booked_services = list(completed_bookings.values_list('service__service_name', 'service__price', 'service__description'))

# #     booked_price_bands = []
# #     booked_prices = []
# #     booked_descriptions = []
# #     booked_service_ids = set()

# #     # Step 1: Group all services by name
# #     services_by_name = defaultdict(list)
# #     for s in Service.objects.all():
# #         services_by_name[s.service_name].append(s)

# #     print("\n📊 All Service Prices by Name:")
# #     for name, services in services_by_name.items():
# #         prices = [float(s.price) for s in services]
# #         print(f"  {name}: {prices}")

# #     for service_name, booked_price, description in booked_services:
# #         booked_prices.append(float(booked_price))
# #         if description:
# #             booked_descriptions.append(description)

# #         related_services = services_by_name[service_name]
# #         if len(related_services) < 3:
# #             continue  # Not enough data to band

# #         all_prices = sorted([float(s.price) for s in related_services])
# #         p33 = np.percentile(all_prices, 33)
# #         p66 = np.percentile(all_prices, 66)

# #         if float(booked_price) <= p33:
# #             booked_price_bands.append((service_name, 'low'))
# #         elif float(booked_price) <= p66:
# #             booked_price_bands.append((service_name, 'medium'))
# #         else:
# #             booked_price_bands.append((service_name, 'high'))

# #         print(f"\n🎯 {service_name} | Booked: {booked_price} | P33: {p33}, P66: {p66} => Band: {booked_price_bands[-1][1]}")

# #     # Step 2: Count most frequent band
# #     band_counts = Counter([band for _, band in booked_price_bands])
# #     if not band_counts:
# #         return []

# #     most_common_band = band_counts.most_common(1)[0][0]
# #     print(f"\n🏆 Most Frequent Band Overall: {most_common_band}")

# #     # Step 3: AI-based filtering using service description
# #     recommendations = []
# #     all_services = list(Service.objects.exclude(description=""))
# #     all_descriptions = [s.description for s in all_services]

# #     if booked_descriptions and all_descriptions:
# #         user_embedding = model.encode(booked_descriptions, convert_to_tensor=True).mean(dim=0)
# #         all_embeddings = model.encode(all_descriptions, convert_to_tensor=True)

# #         cos_scores = util.cos_sim(user_embedding, all_embeddings)[0].cpu().numpy()
# #         sorted_indices = np.argsort(-cos_scores)[:20]  # top 20

# #         for idx in sorted_indices:
# #             s = all_services[int(idx)]  # Ensure idx is an int, not a Tensor
# #             recommendations.append(s)

# #     # Step 4: Filter only those that match most common band for each service name
# #     final_recommendations = []
# #     for service in recommendations:
# #         group = services_by_name[service.service_name]
# #         if len(group) < 3:
# #             continue

# #         prices = sorted([float(s.price) for s in group])
# #         p33 = np.percentile(prices, 33)
# #         p66 = np.percentile(prices, 66)

# #         price = float(service.price)
# #         band = 'low' if price <= p33 else 'medium' if price <= p66 else 'high'

# #         if band == most_common_band:
# #             final_recommendations.append(service)

# #     # Add the booked services back to recommendations
# #     booked_services_models = Booking.objects.filter(client=user, status="Completed").values_list('service', flat=True).distinct()
# #     booked_service_objs = Service.objects.filter(id__in=booked_services_models)
# #     for s in booked_service_objs:
# #         if s not in final_recommendations:
# #             final_recommendations.append(s)

# #     print("\n✅ Final Recommended Services:", [s.service_name for s in final_recommendations])
# #     return final_recommendations

# from collections import defaultdict, Counter
# import numpy as np
# from sklearn.cluster import KMeans
# from sentence_transformers import SentenceTransformer, util
# from .models import Booking, Service

# # Load sentence-transformer model once
# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# def recommend_services_ai_price_band(user):
#     completed_bookings = Booking.objects.filter(client=user, status="Completed")
#     print("\n✅ Completed Bookings:", completed_bookings.count())

#     if completed_bookings.count() < 1:
#         return []

#     booked_services = list(completed_bookings.values_list('service__service_name', 'service__price', 'service__description'))
#     booked_descriptions = []

#     # Step 1: Group all services by name
#     services_by_name = defaultdict(list)
#     for s in Service.objects.exclude(description=""):
#         services_by_name[s.service_name].append(s)

#     # Step 2: KMeans price banding within each service name group
#     service_band_map = {}
#     for name, services in services_by_name.items():
#         prices = np.array([[float(s.price)] for s in services])
#         if len(services) < 3:
#             # Too few to cluster — mark as medium
#             for s in services:
#                 service_band_map[s.id] = 'medium'
#             continue

#         kmeans = KMeans(n_clusters=3, random_state=42)
#         kmeans.fit(prices)
#         centroids = kmeans.cluster_centers_.flatten()
#         sorted_clusters = np.argsort(centroids)
#         label_map = {
#             sorted_clusters[0]: 'low',
#             sorted_clusters[1]: 'medium',
#             sorted_clusters[2]: 'high'
#         }

#         for i, s in enumerate(services):
#             band = label_map[kmeans.labels_[i]]
#             service_band_map[s.id] = band

#     # Step 3: Identify most frequently booked band(s)
#     booked_price_bands = []
#     for service_name, booked_price, description in booked_services:
#         if description:
#             booked_descriptions.append(description)

#         matched_services = [
#             s for s in services_by_name[service_name]
#             if float(s.price) == float(booked_price)
#         ]
#         if not matched_services:
#             continue
#         s = matched_services[0]
#         band = service_band_map.get(s.id)
#         if band:
#             booked_price_bands.append(band)
#             print(f"🎯 {service_name} | Booked: {booked_price} => Band: {band}")

#     if not booked_price_bands:
#         return []

#     # Most frequent band(s) overall
#     band_counter = Counter(booked_price_bands)
#     most_common_band = band_counter.most_common(1)[0][0]
#     print(f"\n🏆 Most Frequent Band (AI): {most_common_band}")

#     # Step 4: AI-powered semantic matching
#     all_services = list(Service.objects.exclude(description=""))
#     all_descriptions = [s.description for s in all_services]
#     recommendations = []

#     if booked_descriptions and all_descriptions:
#         user_embedding = model.encode(booked_descriptions, convert_to_tensor=True).mean(dim=0)
#         all_embeddings = model.encode(all_descriptions, convert_to_tensor=True)
#         cos_scores = util.cos_sim(user_embedding, all_embeddings)[0].cpu().numpy()
#         sorted_indices = np.argsort(-cos_scores)[:20]  # Top 20 similar

#         for idx in sorted_indices:
#             s = all_services[int(idx)]
#             recommendations.append(s)

#     # Step 5: Filter by matching price band (not just service name)
#     final_recommendations = []
#     for service in recommendations:
#         band = service_band_map.get(service.id)
#         if band == most_common_band:
#             final_recommendations.append(service)

#     # Step 6: Optionally include already booked services
#     booked_ids = Booking.objects.filter(
#         client=user, status="Completed"
#     ).values_list('service', flat=True).distinct()

#     booked_services_objs = Service.objects.filter(id__in=booked_ids)
#     for s in booked_services_objs:
#         if s not in final_recommendations:
#             final_recommendations.append(s)

#     print("\n✅ Final Recommended Services:", [s.service_name for s in final_recommendations])
#     return final_recommendations
from collections import defaultdict, Counter
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer, util
from .models import Booking, Service

# Load sentence-transformer model once
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def recommend_services_ai_price_band(user):
    completed_bookings = Booking.objects.filter(client=user, status="Completed")
    print("\n✅ Completed Bookings:", completed_bookings.count())

    if completed_bookings.count() < 1:
        return []

    booked_services = list(completed_bookings.values_list('service__service_name', 'service__price', 'service__description'))
    booked_descriptions = []

    # Step 1: Group all services by name
    services_by_name = defaultdict(list)
    for s in Service.objects.exclude(description=""):
        services_by_name[s.service_name].append(s)

    # Step 2: Dynamic Price Banding within each service name group
    service_band_map = {}
    for name, services in services_by_name.items():
        prices = np.array([[float(s.price)] for s in services])
        unique_prices = sorted(set(prices.flatten()))

        # Dynamically determine number of clusters based on distinct prices
        num_clusters = len(unique_prices)
        if num_clusters < 2:
            num_clusters = 2  # At least 2 bands (low, high) if there are too few prices

        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(prices)
        centroids = kmeans.cluster_centers_.flatten()
        sorted_clusters = np.argsort(centroids)

        # Dynamically map clusters to price bands
        label_map = {}
        for idx, cluster in enumerate(sorted_clusters):
            label_map[cluster] = f'band_{idx+1}'

        # Assign services to corresponding price bands
        for i, s in enumerate(services):
            band = label_map[kmeans.labels_[i]]
            service_band_map[s.id] = band

    # Step 3: Identify most frequently booked band(s)
    booked_price_bands = []
    for service_name, booked_price, description in booked_services:
        if description:
            booked_descriptions.append(description)

        matched_services = [
            s for s in services_by_name[service_name]
            if float(s.price) == float(booked_price)
        ]
        if not matched_services:
            continue
        s = matched_services[0]
        band = service_band_map.get(s.id)
        if band:
            booked_price_bands.append(band)
            print(f"🎯 {service_name} | Booked: {booked_price} => Band: {band}")

    if not booked_price_bands:
        return []

    # Most frequent band(s) overall
    band_counter = Counter(booked_price_bands)
    most_common_band = band_counter.most_common(1)[0][0]
    print(f"\n🏆 Most Frequent Band (AI): {most_common_band}")

    # Step 4: AI-powered semantic matching
    all_services = list(Service.objects.exclude(description=""))
    all_descriptions = [s.description for s in all_services]
    recommendations = []

    if booked_descriptions and all_descriptions:
        user_embedding = model.encode(booked_descriptions, convert_to_tensor=True).mean(dim=0)
        all_embeddings = model.encode(all_descriptions, convert_to_tensor=True)
        cos_scores = util.cos_sim(user_embedding, all_embeddings)[0].cpu().numpy()
        sorted_indices = np.argsort(-cos_scores)[:20]  # Top 20 similar

        for idx in sorted_indices:
            s = all_services[int(idx)]
            recommendations.append(s)

    # Step 5: Filter by matching price band (not just service name)
    final_recommendations = []
    for service in recommendations:
        band = service_band_map.get(service.id)
        if band == most_common_band:
            final_recommendations.append(service)

    # Step 6: Optionally include already booked services
    booked_ids = Booking.objects.filter(
        client=user, status="Completed"
    ).values_list('service', flat=True).distinct()

    booked_services_objs = Service.objects.filter(id__in=booked_ids)
    for s in booked_services_objs:
        if s not in final_recommendations:
            final_recommendations.append(s)

    print("\n✅ Final Recommended Services:", [s.service_name for s in final_recommendations])
    return final_recommendations
